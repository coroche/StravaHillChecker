from flask import request, render_template_string, redirect, url_for
from data.config import getEmailTemplate
from data import config
from library.smtp import sendEmail


def serve_form():
    
    error=None
    if request.method == 'POST':
        try:
            email = request.form['email']
            onStrava = request.form['onStrava'] == 'yes'
            firstname = request.form['firstName']
            surname = request.form['surname']

            success, message, id = config.createReceipient(email, onStrava, firstname, surname)
            if not success:
                error=message
            else:
                receipient = config.getReceipient(id)
                email_html = config.getEmailTemplate('verificationEmail.html')
                settings = config.getConfig()
                verificationLink = f'{settings.google_functions_url}/subscribe/verify?id={receipient.id}&token={receipient.verification_token}'
                email_html = email_html\
                    .replace('{VerificationLink}', verificationLink)\
                    .replace('{BackgroundImage}', settings.default_email_image)
                
                sendEmail(email_html, receipient.email, 'Verify your email')

                return render_template_string(getEmailTemplate('message.html'), message = f'A verification link has been sent to {email}.')
        except Exception as e:
            return f'Error submitting form data: {str(e)}', 500
    
    return render_template_string(getEmailTemplate('subscribeForm.html'), error=error)


def verify_email():
    
    verification_token = request.args.get('token')
    receipient_id = request.args.get('id')
    message = 'Verification failed'
    
    if verification_token and receipient_id:
        receipient = config.getReceipient(receipient_id)
        if receipient and verification_token == receipient.verification_token:
            config.verifyReceipientEmail(receipient.id)
            message = 'Email verified'
  
    return render_template_string(getEmailTemplate('message.html'), message = message)


def gcf_entry_point(request):

    if request.path == '/verify': 
        return verify_email()
    else:
        return serve_form()
