# python3-mimplesail
Python `email`/`smtplib` wrapper module for simple email sending including attachments and inline images.

## Usage

```python
import mimplesail

# create mailer
mailer = mimplesail.Mailer( 
    server   = "mail.server.com",
    port     = 587,
    email    = "address@server.com",
    password = "thepassword",
    )

# create an html body text
htmlbody = """
Hey!<p>
This is the HTML Mail text.<p>
You can add inline images: <img src="cid:inlineimage.png"> <p>
"""

# add all content
mailer.add_html(htmlbody) # add the html body
mailer.add_inline_image("temp/inlineimage.png") # add the inline image
mailer.add_attachment_image("temp/attachmentimage.png") # add an attachment image

# send the email
mailer.send(
  subject = "Mail sent with mimplesail Python module",
  recipient = "receipient@server.com"
  )
```

