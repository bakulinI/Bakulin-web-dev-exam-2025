from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from math import ceil
from app.blueprints.auth import public_route
from functools import wraps
from werkzeug.utils import secure_filename
import os
import bleach
from app.repositories.animal_repository import AnimalRepository
from app.repositories.photo_repository import PhotoRepository
from app.decorators import admin_required, moderator_required
import mysql.connector

bp = Blueprint('animals', __name__, url_prefix='/animals')

def init_app(app):
    bp.animal_repository = AnimalRepository(app.db)
    bp.photo_repository = PhotoRepository(app.db)

@bp.route('/')
def index():
    """Главная страница со списком животных"""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    status = request.args.get('status')
    
    per_page = 9  # Количество животных на странице
    animals = bp.animal_repository.get_paginated(page, sort_by, sort_order, status)
    total = bp.animal_repository.get_total_count(status)
    total_pages = (total + per_page - 1) // per_page  # Округление вверх
    
    return render_template(
        'animals/index.html',
        animals=animals,
        total=total,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        sort_order=sort_order,
        status=status
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Страница добавления нового животного"""
    if request.method == 'POST':
        try:
            # Получаем и очищаем данные формы
            name = bleach.clean(request.form['name'])
            description = bleach.clean(request.form['description'])
            age_months = int(request.form['age_months'])
            breed = bleach.clean(request.form['breed'])
            gender = request.form['gender']
            status = request.form['status']
            
            # Проверяем наличие фотографий
            if 'photos' not in request.files:
                flash('Необходимо загрузить хотя бы одну фотографию', 'danger')
                return render_template('animals/create.html', form=request.form)
            
            photos = request.files.getlist('photos')
            if not photos or not photos[0].filename:
                flash('Необходимо загрузить хотя бы одну фотографию', 'danger')
                return render_template('animals/create.html', form=request.form)
            
            # Сохраняем животное и фотографии в транзакции
            connection = bp.animal_repository.db.connect()
            try:
                connection.start_transaction()
                
                # Создаем животное
                animal_id = bp.animal_repository.create({
                    'name': name,
                    'description': description,
                    'age_months': age_months,
                    'breed': breed,
                    'gender': gender,
                    'status': status
                })
                
                # Сохраняем фотографии
                for photo in photos:
                    if photo.filename:
                        filename = secure_filename(photo.filename)
                        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        photo.save(photo_path)
                        
                        bp.photo_repository.create({
                            'animal_id': animal_id,
                            'filename': filename
                        })
                
                connection.commit()
                flash('Животное успешно добавлено', 'success')
                return redirect(url_for('animals.view', id=animal_id))
                
            except Exception as e:
                connection.rollback()
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
    """Страница редактирования животного"""
    animal = bp.animal_repository.get_by_id(id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    if request.method == 'POST':
        try:
            # Получаем и очищаем данные формы
            name = bleach.clean(request.form['name'])
            description = bleach.clean(request.form['description'])
            age_months = int(request.form['age_months'])
            breed = bleach.clean(request.form['breed'])
            gender = request.form['gender']
            status = request.form['status']
            
            # Обновляем данные животного
            connection = bp.animal_repository.db.connect()
            try:
                connection.start_transaction()
                
                bp.animal_repository.update(id, {
                    'name': name,
                    'description': description,
                    'age_months': age_months,
                    'breed': breed,
                    'gender': gender,
                    'status': status
                })
                
                connection.commit()
                flash('Данные животного успешно обновлены', 'success')
                return redirect(url_for('animals.view', id=id))
                
            except Exception as e:
                connection.rollback()
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
    """Страница просмотра информации о животном"""
    animal = bp.animal_repository.get_by_id(id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    photos = bp.photo_repository.get_by_animal_id(id)
    return render_template('animals/view.html', animal=animal, photos=photos)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """Удаление животного"""
    animal = bp.animal_repository.get_by_id(id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    try:
        connection = bp.animal_repository.db.connect()
        try:
            connection.start_transaction()
            
            # Удаляем фотографии
            photos = bp.photo_repository.get_by_animal_id(id)
            for photo in photos:
                photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo['filename'])
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                bp.photo_repository.delete(photo['id'])
            
            # Удаляем животное
            bp.animal_repository.delete(id)
            
            connection.commit()
            flash('Животное успешно удалено', 'success')
            
        except Exception as e:
            connection.rollback()
            current_app.logger.error(f"Error deleting animal: {str(e)}")
            flash('При удалении животного возникла ошибка', 'danger')
        finally:
            connection.close()
            
    except Exception as e:
        current_app.logger.error(f"Error processing delete request: {str(e)}")
        flash('При удалении животного возникла ошибка', 'danger')
    
    return redirect(url_for('animals.index'))