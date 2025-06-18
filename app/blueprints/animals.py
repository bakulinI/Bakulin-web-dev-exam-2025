from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import bleach
from app.repositories.animal_repository import AnimalRepository
from app.repositories.photo_repository import PhotoRepository
from app.decorators import admin_required, moderator_required

bp = Blueprint('animals', __name__, url_prefix='/animals')

def init_app(app):
    bp.animal_repository = AnimalRepository(app.db)
    bp.photo_repository = PhotoRepository(app.db)
    bp.adoption_repository = app.adoption_repository

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    animals = bp.animal_repository.get_paginated(page)
    total = bp.animal_repository.get_total_count()
    total_pages = (total + per_page - 1) // per_page
    return render_template(
        'animals/index.html',
        animals=animals,
        total=total,
        page=page,
        total_pages=total_pages
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        try:
            name = bleach.clean(request.form['name'])
            description = bleach.clean(request.form['description'])
            age_months = int(request.form['age_months'])
            breed = bleach.clean(request.form['breed'])
            gender = request.form['gender']
            status = request.form['status']

            if 'photos' not in request.files:
                flash('Необходимо загрузить хотя бы одну фотографию', 'danger')
                return render_template('animals/create.html', form=request.form)
            
            photos = request.files.getlist('photos')
            if not photos or not photos[0].filename:
                flash('Необходимо загрузить хотя бы одну фотографию', 'danger')
                return render_template('animals/create.html', form=request.form)

            connection = bp.animal_repository.db.connect()
            try:
                animal_id = bp.animal_repository.create({
                    'name': name,
                    'description': description,
                    'age_months': age_months,
                    'breed': breed,
                    'gender': gender,
                    'status': status
                })

                for photo in photos:
                    if photo.filename:
                        filename = secure_filename(photo.filename)
                        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        photo.save(photo_path)
                        
                        bp.photo_repository.create({
                            'animal_id': animal_id,
                            'filename': filename,
                            'mime_type': photo.content_type
                        })
                
                flash('Животное успешно добавлено', 'success')
                return redirect(url_for('animals.view', id=animal_id))
                
            except Exception as e:
                current_app.logger.error(f"Error creating animal: {str(e)}")
                flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
                return render_template('animals/create.html', form=request.form)
            finally:
                connection.close()
                
        except Exception as e:
            current_app.logger.error(f"Error processing form: {str(e)}")
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('animals/create.html', form=request.form)
    
    return render_template('animals/create.html', form={})

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@moderator_required
def edit(id):
    animal = bp.animal_repository.get_by_id(id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    if request.method == 'POST':
        try:
            name = bleach.clean(request.form['name'])
            description = bleach.clean(request.form['description'])
            age_months = int(request.form['age_months'])
            breed = bleach.clean(request.form['breed'])
            gender = request.form['gender']
            status = request.form['status']

            connection = bp.animal_repository.db.connect()
            try:
                bp.animal_repository.update(id, {
                    'name': name,
                    'description': description,
                    'age_months': age_months,
                    'breed': breed,
                    'gender': gender,
                    'status': status
                }, connection=connection)
                connection.commit()
                
                flash('Данные животного успешно обновлены', 'success')
                return redirect(url_for('animals.view', id=id))
                
            except Exception as e:
                current_app.logger.error(f"Error updating animal: {str(e)}")
                flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
                return render_template('animals/edit.html', form=request.form, animal=animal)
            finally:
                connection.close()
                
        except Exception as e:
            current_app.logger.error(f"Error processing form: {str(e)}")
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('animals/edit.html', form=request.form, animal=animal)
    
    return render_template('animals/edit.html', form=animal, animal=animal)

@bp.route('/<int:id>')
def view(id):
    animal = bp.animal_repository.get_by_id(id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    photos = bp.photo_repository.get_by_animal_id(id)

    adoptions = []
    user_adoption = None
    
    if current_user.is_authenticated:
        if current_user.role_name in ['admin', 'moderator']:
            adoptions = bp.adoption_repository.get_by_animal_id(id)
        elif current_user.role_name == 'user':
            user_adoption = bp.adoption_repository.get_by_user_and_animal(current_user.id, id)
    
    return render_template('animals/view.html', 
                         animal=animal, 
                         photos=photos, 
                         adoptions=adoptions,
                         user_adoption=user_adoption)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    animal = bp.animal_repository.get_by_id(id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    try:
        connection = bp.adoption_repository.db_connector.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM adoptions WHERE animal_id = %s", (id,))
            connection.commit()
            cursor.close()
        except Exception as e:
            connection.rollback()
            current_app.logger.error(f"Error deleting adoptions: {str(e)}")
        finally:
            connection.close()

        photos = bp.photo_repository.get_by_animal_id(id)
        for photo in photos:
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo['filename'])
            if os.path.exists(photo_path):
                os.remove(photo_path)
            bp.photo_repository.delete(photo['id'])

        bp.animal_repository.delete(id)
        
        flash('Животное успешно удалено', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error deleting animal: {str(e)}")
        flash('При удалении животного возникла ошибка', 'danger')
    
    return redirect(url_for('animals.index'))

@bp.route('/<int:id>/submit_adoption', methods=['POST'])
@login_required
def submit_adoption(id):
    animal = bp.animal_repository.get_by_id(id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))

    if animal['status'] not in ['available', 'adoption']:
        flash('Это животное недоступно для усыновления', 'warning')
        return redirect(url_for('animals.view', id=id))
    
    contact_info = bleach.clean(request.form['contact_info'])
    
    try:
        existing_adoption = bp.adoption_repository.get_by_user_and_animal(current_user.id, id)
        if existing_adoption:
            flash('Вы уже подавали заявку на усыновление этого животного', 'warning')
            return redirect(url_for('animals.view', id=id))

        adoption_id = bp.adoption_repository.create({
            'animal_id': id,
            'user_id': current_user.id,
            'contact_info': contact_info
        })
        
        flash('Заявка на усыновление успешно подана', 'success')
        return redirect(url_for('animals.view', id=id))
        
    except Exception as e:
        current_app.logger.error(f"Error submitting adoption: {str(e)}")
        flash('При подаче заявки возникла ошибка', 'danger')
        return redirect(url_for('animals.view', id=id))

@bp.route('/<int:id>/adoptions')
@login_required
@moderator_required
def get_adoptions(id):
    try:
        adoptions = bp.adoption_repository.get_by_animal_id(id)
        return {'adoptions': adoptions}
    except Exception as e:
        current_app.logger.error(f"Error getting adoptions: {str(e)}")
        return {'error': 'Ошибка при получении заявок'}, 500

@bp.route('/adoption/<int:adoption_id>/approve', methods=['POST'])
@login_required
@moderator_required
def approve_adoption(adoption_id):
    try:
        bp.adoption_repository.update_status(adoption_id, 'accepted')
        flash('Заявка на усыновление одобрена', 'success')
    except Exception as e:
        current_app.logger.error(f"Error approving adoption: {str(e)}")
        flash('При одобрении заявки возникла ошибка', 'danger')
    
    return redirect(request.referrer or url_for('animals.index'))

@bp.route('/adoption/<int:adoption_id>/reject', methods=['POST'])
@login_required
@moderator_required
def reject_adoption(adoption_id):
    try:
        bp.adoption_repository.update_status(adoption_id, 'rejected')
        flash('Заявка на усыновление отклонена', 'success')
    except Exception as e:
        current_app.logger.error(f"Error rejecting adoption: {str(e)}")
        flash('При отклонении заявки возникла ошибка', 'danger')
    
    return redirect(request.referrer or url_for('animals.index'))