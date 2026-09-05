from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import uuid
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# 🔥 ALL MODELS
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'staff', 'client'), default='staff')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Parcel(db.Model):
    __tablename__ = 'parcels'
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    sender_name = db.Column(db.String(100))
    sender_address = db.Column(db.Text)
    sender_mobile = db.Column(db.String(15))
    receiver_name = db.Column(db.String(100))
    receiver_address = db.Column(db.Text)
    receiver_mobile = db.Column(db.String(15))
    parcel_type = db.Column(db.String(50))
    parcel_name = db.Column(db.String(100))
    out_date = db.Column(db.Date)
    expected_delivery = db.Column(db.Date)
    delivered_date = db.Column(db.Date)
    status = db.Column(db.Enum('pending', 'picked', 'in_transit', 'out_for_delivery', 'delivered', 'cancelled'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'))
    amount = db.Column(db.Float)
    payment_type = db.Column(db.Enum('cod', 'online'))
    status = db.Column(db.Enum('pending', 'completed', 'failed'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 🔥 AUTO-ASSIGN DEMO PARCELS TO LOGGED USER
@app.before_request
def assign_demo_parcels():
    if 'user_id' in session:
        # Assign demo parcels to current user if empty
        user_parcels_count = db.session.query(Parcel).filter_by(user_id=session['user_id']).count()
        if user_parcels_count == 0:
            demo_parcel_ids = [1, 2, 3]  # Your demo XSHIP001,002,003
            for pid in demo_parcel_ids:
                parcel = Parcel.query.get(pid)
                if parcel and not parcel.user_id:
                    parcel.user_id = session['user_id']
            db.session.commit()

# DECORATORS
def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

# ROUTES
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form['password'].strip()
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.name
            flash(f'Welcome {user.name}!')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    # 🔥 FRESH DATA - YOUR PARCELS ONLY
    user_parcels = Parcel.query.filter_by(user_id=session['user_id']).all()
    
    stats = {
        'total': len(user_parcels),
        'delivered': len([p for p in user_parcels if p.status == 'delivered']),
        'pending': len([p for p in user_parcels if p.status == 'pending']),
        'in_transit': len([p for p in user_parcels if p.status in ['picked', 'in_transit', 'out_for_delivery']]),
        'cancelled': len([p for p in user_parcels if p.status == 'cancelled'])
    }
    
    parcels = sorted(user_parcels, key=lambda p: p.created_at, reverse=True)[:10]
    
    return render_template('dashboard.html', stats=stats, parcels=parcels,
                         user_name=session.get('user_name'), user_role=session.get('user_role'))
@app.route('/shipments')
@login_required
def shipments():
    page = request.args.get('page', 1, type=int)
    parcels = Parcel.query.order_by(Parcel.id.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('shipments.html', parcels=parcels,
                         user_name=session.get('user_name'), user_role=session.get('user_role'))

@app.route('/add_parcel', methods=['GET', 'POST'])
@login_required
def add_parcel():
    if request.method == 'POST':
        tracking_number = f"XSHIP{uuid.uuid4().hex[:6].upper()}"
        parcel = Parcel(
            tracking_number=tracking_number,
            sender_name=request.form['sender_name'],
            sender_address=request.form['sender_address'],
            sender_mobile=request.form['sender_mobile'],
            receiver_name=request.form['receiver_name'],
            receiver_address=request.form['receiver_address'],
            receiver_mobile=request.form['receiver_mobile'],
            parcel_type=request.form['parcel_type'],
            parcel_name=request.form['parcel_name'],
            out_date=request.form.get('out_date'),
            expected_delivery=request.form.get('expected_delivery'),
            user_id=session['user_id']
        )
        db.session.add(parcel)
        db.session.commit()
        
        # 🔥 INSTANT SUCCESS + REDIRECT TO DASHBOARD
        flash(f'✅ Parcel {tracking_number} created! Dashboard updated.', 'success')
        return redirect(url_for('dashboard'))  # ← GO TO DASHBOARD
    
    return render_template('add_parcel.html', user_name=session.get('user_name'))
@app.route('/update_status/<int:parcel_id>', methods=['POST'])
@login_required
def update_status(parcel_id):
    parcel = Parcel.query.get_or_404(parcel_id)
    new_status = request.json['status']
    parcel.status = new_status
    if new_status == 'delivered':
        parcel.delivered_date = date.today()
    db.session.commit()
    return jsonify({'success': True, 'status': new_status})

@app.route('/delete_parcel/<int:parcel_id>', methods=['DELETE'])
@login_required
def delete_parcel(parcel_id):
    parcel = Parcel.query.get_or_404(parcel_id)
    db.session.delete(parcel)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/tracking')
@login_required
def tracking_page():
    return render_template('tracking.html', parcel=None,
                         user_name=session.get('user_name'), user_role=session.get('user_role'))

@app.route('/tracking/<tracking_number>')
@login_required
def tracking(tracking_number):
    parcel = Parcel.query.filter_by(tracking_number=tracking_number.upper()).first()
    if not parcel:
        flash('Tracking number not found')
        return redirect(url_for('tracking_page'))
    return render_template('tracking.html', parcel=parcel,
                         user_name=session.get('user_name'), user_role=session.get('user_role'))

@app.route('/delivery')
@login_required
def delivery():
    parcels = Parcel.query.filter(Parcel.status.in_(['pending', 'picked', 'in_transit'])).all()
    return render_template('delivery.html', parcels=parcels,
                         user_name=session.get('user_name'), user_role=session.get('user_role'))

# 🔥 DELETE ALL DEMO DATA - RUN ONCE
@app.route('/reset_demo')
def reset_demo():
    # Delete all parcels, payments, users (except admin)
    Parcel.query.delete()
    Payment.query.delete()
    User.query.filter(User.email != 'admin@xship.com').delete()
    db.session.commit()
    
    # Create admin only
    admin = User(name='Admin', email='admin@xship.com', password='admin123', role='admin')
    db.session.add(admin)
    db.session.commit()
    
    return jsonify({'message': '✅ Demo data deleted! Fresh start. Login: admin@xship.com/admin123'})

@app.route('/analytics')
@login_required
def analytics():
    user_parcels = Parcel.query.filter_by(user_id=session['user_id']).all()
    
    # Safe monthly data
    monthly_data = {}
    for parcel in user_parcels[-12:]:  # Last 12 parcels
        month = parcel.created_at.strftime('%b')
        monthly_data[month] = monthly_data.get(month, 0) + 1
    
    analytics_data = {
        'total_parcels': len(user_parcels),
        'monthly_shipments': monthly_data,
        'status_counts': {
            'delivered': len([p for p in user_parcels if p.status == 'delivered']),
            'pending': len([p for p in user_parcels if p.status == 'pending']),
            'in_transit': len([p for p in user_parcels if p.status in ['picked', 'in_transit', 'out_for_delivery']])
        }
    }
    
    return render_template('analytics.html', analytics_data=analytics_data,
                         user_name=session.get('user_name'), user_role=session.get('user_role'))

@app.route('/receipt/<int:payment_id>')
@login_required
def receipt(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    parcel = Parcel.query.get(payment.parcel_id)
    
    sender_mobile = parcel.sender_mobile if parcel and parcel.sender_mobile else ''
    status_class = 'completed' if payment.status == 'completed' else 'pending'
    status_text = 'COMPLETED' if payment.status == 'completed' else 'PENDING'
    payment_type_text = 'Cash on Delivery' if payment.payment_type == 'cod' else 'Online Payment'
    
    receipt_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Receipt #{payment.id} - XShip</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif; 
            max-width: 650px; margin: 40px auto; 
            padding: 2.5rem; background: white; 
            border-radius: 24px; 
            box-shadow: 0 25px 70px rgba(0,0,0,0.15); 
            line-height: 1.7; color: #2d3748;
        }}
        .header {{ 
            text-align: center; 
            border-bottom: 4px solid #667eea; 
            padding-bottom: 1.8rem; 
            margin-bottom: 2.5rem; 
        }}
        .logo {{ 
            font-size: 2.5rem; 
            color: #667eea; 
            font-weight: 800; 
            margin-bottom: 0.8rem; 
        }}
        .amount {{ 
            font-size: 3.2rem; 
            font-weight: 800; 
            color: #2ed573; 
            text-align: center; 
            padding: 2.5rem; 
            background: linear-gradient(135deg, #f8f9ff, #e8f5e8); 
            border-radius: 25px; 
            margin: 2.5rem 0; 
            box-shadow: 0 15px 40px rgba(46,213,115,0.2);
        }}
        .details {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 2.5rem; 
            margin: 2.5rem 0; 
        }}
        .status-completed {{ 
            color: #2ed573; 
            font-weight: bold; 
            font-size: 1.1rem; 
            padding: 0.4rem 1rem; 
            background: rgba(46,213,115,0.1); 
            border-radius: 20px;
        }}
        .status-pending {{ 
            color: #ffa502; 
            font-weight: bold; 
            font-size: 1.1rem; 
            padding: 0.4rem 1rem; 
            background: rgba(255,165,2,0.1); 
            border-radius: 20px;
        }}
        .footer {{ 
            text-align: center; 
            color: #64748b; 
            padding-top: 2.5rem; 
            border-top: 2px dashed #e2e8f0; 
            margin-top: 3rem; 
        }}
        h3 {{ 
            color: #2d3748; 
            margin-bottom: 1.2rem; 
            font-size: 1.4rem; 
            font-weight: 700;
        }}
        p {{ 
            margin: 1rem 0; 
            font-size: 1rem;
        }}
        strong {{ 
            color: #2d3748; 
            font-weight: 700;
        }}
        @media print {{ body {{ box-shadow: none; margin: 0; }} }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">XShip</div>
        <h2>Payment Receipt</h2>
        <div style="font-size: 1rem; opacity: 0.8;">Official Receipt Document</div>
    </div>
    
    <div class="details">
        <div>
            <h3>Shipment Details</h3>
            <p><strong>Tracking Number:</strong><br>{parcel.tracking_number if parcel else 'N/A'}</p>
            <p><strong>Sender Name:</strong><br>{parcel.sender_name if parcel else 'N/A'}</p>
            <p><strong>Receiver Name:</strong><br>{parcel.receiver_name if parcel else 'N/A'}</p>
            {f'<p><strong>Sender Mobile:</strong><br>{sender_mobile}</p>' if sender_mobile and sender_mobile != 'N/A' else ''}
        </div>
        <div>
            <h3>Payment Details</h3>
            <p><strong>Receipt Number:</strong><br>#REC-{payment.id}</p>
            <p><strong>Payment Type:</strong><br>{payment_type_text}</p>
            <p><strong>Status:</strong><br><span class="status-{status_class}">{status_text}</span></p>
            <p><strong>Payment Date:</strong><br>{payment.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
    </div>
    
    <div class="amount">
        <div style="font-size: 1.3rem; margin-bottom: 1rem; color: #64748b; font-weight: 600;">Payment Amount</div>
        <div style="font-size: 0.9rem; color: #718096; margin-bottom: 0.5rem;">In Indian Rupees (INR)</div>
        Rs. {payment.amount:,.2f}
    </div>
    
    <div class="footer">
        <div style="font-size: 1.1rem; margin-bottom: 1rem; color: #2d3748;">
            Thank you for choosing XShip!
        </div>
        <p><strong>Service:</strong> Fast - Reliable - Secure Delivery</p>
        <p style="font-size: 0.9rem; opacity: 0.8;">
            This is a computer-generated receipt. No signature required.
        </p>
        <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0; font-size: 0.85rem;">
            XShip Courier Services | support@xship.com | +91-XXXXXXXXXX
        </div>
    </div>
</body>
</html>
"""
    return receipt_html, 200, {
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Disposition': f'inline; filename="xship-receipt-{payment.id}.html"'
    }

@app.route('/payments')
@login_required
def payments():
    # 🔥 AUTO-GENERATE PAYMENTS FOR NEW PARCELS (REAL DATA ONLY)
    parcels_without_payment = Parcel.query.filter(
        ~Parcel.id.in_(db.session.query(Payment.parcel_id).distinct())
    ).all()
    
    # Create payments for parcels without payments
    for parcel in parcels_without_payment:
        # SMART AMOUNT BASED ON PARCEL TYPE
        base_amount = 100.0
        if parcel.parcel_type == 'document':
            amount = 50.0
        elif parcel.parcel_type == 'fragile':
            amount = 250.0
        elif parcel.parcel_type == 'electronics':
            amount = 350.0
        else:  # parcel
            amount = base_amount
        
        # Add weight/distance factor (random realistic)
        import random
        weight_factor = random.uniform(1.0, 2.0)
        amount = round(amount * weight_factor, 2)
        
        payment = Payment(
            parcel_id=parcel.id,
            amount=amount,
            payment_type='cod' if random.choice([True, False]) else 'online',
            status='pending' if random.choice([True, False]) else 'completed'
        )
        db.session.add(payment)
    
    db.session.commit()
    
    # Get all payments with parcel details
    payments = Payment.query.all()
    payment_list = []
    total_revenue = 0
    pending_amount = 0
    
    for payment in payments:
        parcel = Parcel.query.get(payment.parcel_id)
        if parcel:
            payment_list.append({
                'id': payment.id,
                'parcel_id': payment.parcel_id,
                'tracking_number': parcel.tracking_number,
                'parcel_type': parcel.parcel_type or 'Standard',
                'amount': payment.amount,
                'payment_type': payment.payment_type,
                'status': payment.status,
                'created_at': payment.created_at,
                'sender_name': parcel.sender_name,
                'receiver_name': parcel.receiver_name
            })
            total_revenue += payment.amount
            if payment.status == 'pending':
                pending_amount += payment.amount
    
    # Stats for dashboard
    stats = {
        'total_payments': len(payment_list),
        'total_revenue': round(total_revenue, 2),
        'pending_amount': round(pending_amount, 2),
        'completed_count': len([p for p in payment_list if p['status'] == 'completed'])
    }
    
    return render_template('payments.html', 
                         payments=payment_list, 
                         stats=stats,
                         user_name=session.get('user_name'), 
                         user_role=session.get('user_role'))


@app.route('/api/stats')
@login_required
def api_stats():
    # 🔥 ULTRA-FAST QUERY - YOUR PARCELS ONLY
    stats = db.session.query(
        db.func.count(Parcel.id).label('total'),
        db.func.count(Parcel.id).filter(Parcel.status == 'delivered').label('delivered'),
        db.func.count(Parcel.id).filter(Parcel.status == 'pending').label('pending'),
        db.func.count(Parcel.id).filter(Parcel.status.in_(['picked', 'in_transit', 'out_for_delivery'])).label('in_transit'),
        db.func.count(Parcel.id).filter(Parcel.status == 'cancelled').label('cancelled')
    ).filter(
        Parcel.user_id == session['user_id']
    ).first()
    
    return jsonify({
        'total': stats.total,
        'delivered': stats.delivered,
        'pending': stats.pending,
        'in_transit': stats.in_transit,
        'cancelled': stats.cancelled
    })

if __name__ == '__main__':
    with app.app_context():
        print("✅ Database connected - Ready!")
        print("👥 Users found:", User.query.count())
        print("📦 Parcels found:", Parcel.query.count())
    print("🚀 XShip running: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)