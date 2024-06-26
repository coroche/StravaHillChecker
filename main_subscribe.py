from flask import request, render_template_string, Request, Response
from data.config import getHTMLTemplate
from data import config
from library.smtp import sendEmail


def serve_form():
    
    error=None
    if request.method == 'POST':
        try:
            email = request.form['email'].strip()
            onStrava = request.form['onStrava'] == 'yes'
            firstname = request.form['firstName'].strip()
            surname = request.form['surname'].strip()

            success, message, id = config.createReceipient(email, onStrava, firstname, surname)
            if not success:
                error=message
            else:
                receipient = config.getReceipient(id)
                email_html = config.getHTMLTemplate('verificationEmail.html')
                settings = config.getConfig()
                verificationLink = f'{settings.google_functions_url}/subscribe/verify?id={receipient.id}&token={receipient.verification_token}'
                email_html = email_html\
                    .replace('{VerificationLink}', verificationLink)\
                    .replace('{BackgroundImage}', settings.default_email_image)
                
                sendEmail(email_html, receipient.email, 'Verify your email')

                return render_template_string(getHTMLTemplate('message.html'), message = f'A verification link has been sent to {email}.')
        except Exception as e:
            return Response(f'Error submitting form data: {str(e)}', 500)
    
    return Response(render_template_string(getHTMLTemplate('subscribeForm.html'), error=error), 200)


def verify_email():
    
    verification_token = request.args.get('token')
    receipient_id = request.args.get('id')
    message = 'Verification failed'
    code = 500
    
    if verification_token and receipient_id:
        receipient = config.getReceipient(receipient_id)
        if receipient and verification_token == receipient.verification_token:
            config.verifyReceipientEmail(receipient.id)
            message = 'Email verified'
            code = 200
  
    return Response(render_template_string(getHTMLTemplate('message.html'), message = message), code)

def unsubscribe(subscriberID):
   
    if config.deleteReceipient(subscriberID):
        message = 'You have been unsubscribed and we are no longer friends.'
        code = 200
    else:
        message = 'Subscriber not found'
        code = 404

    return Response(render_template_string(getHTMLTemplate('message.html'), message = message), code)


def gcf_entry_point(request: Request) -> Response:

    if request.path == '/verify': 
        return verify_email()
    
    elif request.path == '/unsubscribe':
        subscriberID = request.args.get('subscriberID')
        return unsubscribe(subscriberID)
    
    else:
        return serve_form()
