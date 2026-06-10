import os
import shutil
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from app import db

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('/backup')
@login_required
def index():
    backup_dir = current_app.config['BACKUP_DIR']
    os.makedirs(backup_dir, exist_ok=True)

    backups = []
    if os.path.exists(backup_dir):
        for f in sorted(os.listdir(backup_dir), reverse=True):
            if f.endswith('.db'):
                fpath = os.path.join(backup_dir, f)
                size = os.path.getsize(fpath)
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                backups.append({'name': f, 'size': size, 'date': mtime})

    # Check last backup reminder
    last_backup_file = current_app.config['LAST_BACKUP_FILE']
    needs_backup = False
    if os.path.exists(last_backup_file):
        with open(last_backup_file, 'r') as f:
            last_str = f.read().strip()
            try:
                last_date = datetime.fromisoformat(last_str)
                if datetime.utcnow() - last_date > timedelta(days=current_app.config['BACKUP_REMINDER_DAYS']):
                    needs_backup = True
            except ValueError:
                needs_backup = True
    else:
        needs_backup = True

    return render_template('backup/index.html', backups=backups, needs_backup=needs_backup)


@backup_bp.route('/backup/download')
@login_required
def download():
    """Create a backup of the current database and send as download."""
    db_path = os.path.join(current_app.instance_path, 'muhasebe.db')
    backup_dir = current_app.config['BACKUP_DIR']
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'muhasebe_{timestamp}.db'
    backup_path = os.path.join(backup_dir, backup_name)

    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)

        # Update last backup time
        with open(current_app.config['LAST_BACKUP_FILE'], 'w') as f:
            f.write(datetime.utcnow().isoformat())

        flash(f'Yedek oluşturuldu: {backup_name}', 'success')
        return send_file(backup_path, as_attachment=True, download_name=backup_name,
                        mimetype='application/octet-stream')
    else:
        flash('Veritabanı bulunamadı.', 'danger')
        return redirect(url_for('backup.index'))


@backup_bp.route('/backup/restore', methods=['POST'])
@login_required
def restore():
    """Restore database from an uploaded backup file."""
    if 'backup_file' not in request.files:
        flash('Dosya seçilmedi.', 'danger')
        return redirect(url_for('backup.index'))

    file = request.files['backup_file']
    if file.filename == '':
        flash('Dosya seçilmedi.', 'danger')
        return redirect(url_for('backup.index'))

    if not file.filename.endswith('.db'):
        flash('Geçersiz dosya formatı. .db uzantılı dosya seçin.', 'danger')
        return redirect(url_for('backup.index'))

    # Create backup of current DB before restoring
    db_path = os.path.join(current_app.instance_path, 'muhasebe.db')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pre_restore_backup = os.path.join(current_app.instance_path, f'pre_restore_{timestamp}.db')
    if os.path.exists(db_path):
        shutil.copy2(db_path, pre_restore_backup)

    # Save uploaded file as current database
    file.save(db_path)
    flash('Veritabanı geri yüklendi. Uygulamayı yeniden başlatmanız gerekebilir.', 'warning')
    return redirect(url_for('dashboard.index'))
