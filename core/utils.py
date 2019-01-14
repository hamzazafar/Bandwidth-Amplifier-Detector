from django.core.mail import EmailMultiAlternatives

def send_mail(subject, from_email, to_emails, html_content=None,
              txt_content=None):
    msg = None
    if html_content:
        msg = EmailMultiAlternatives(subject, '', from_email, to_emails)
        msg.attach_alternative(html_content, "text/html")
    else:
        msg = EmailMultiAlternatives(subject, txt_content, from_email, to_emails)
    msg.send()

