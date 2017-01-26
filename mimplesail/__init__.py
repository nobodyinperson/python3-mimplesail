#/usr/bin/env python
# -*- coding: utf8 -*-
# core modules
import os, sys
# logging
import logging
# email modules
import smtplib
import mimetypes

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
import email.encoders

logger = logging.getLogger(__name__)

# mailer class
class Mailer():
    def __init__(this, server, port, email, password):
        # copy over arguments
        this.server   = server
        this.port     = port
        this.email    = email
        this.password = password

        # initialize internal variables
        this.resetcontent()

        # an SMTP object
        this.connection = smtplib.SMTP()

    def isconnected(this):
        ret = False
        logger.debug("checking connection to mailserver {0}:{1}".format(this.server,this.port))
        try:
            status = this.connection.noop()
            logger.debug("connection is alive")
            ret = True
        except:
            status = -1
            logger.debug("connection is not alive")
            ret = False
        #if status == 250: # only if the right result comes out
            #ret = True
        return ret

    def connect(this):
        logger.debug("attempt to connect to {0}:{1} with TLS".format(this.server,this.port))
        status, message = this.connection.connect( str(this.server) , int(this.port) )
        logger.debug("status: {0}, server responded: {1}".format(status, message))
        this.encryption = "TLS"
        logger.debug("starting TLS encryption")
        try:
            this.connection.starttls()
            logger.debug("successfully started TLS encryption")
        except:
            logger.warning("could not start TLS encryption")
            raise
        logger.debug("logging in with mail {0}".format(this.email))
        try:
            this.login()
            logger.debug("logged in successfully")
        except:
            logger.warning("could not log into email account {0}!".format(this.email))
            raise

    def login(this):
        this.connection.login( this.email, this.password )

    def disconnect(this):
        logger.debug("disconnecting from server {0}".format(this.server))
        this.connection.quit()

    def send(this, subject = None, recipient = None):
        if subject is not None:
            this.subject = subject
        if recipient is not None:
            this.recipient = recipient

        # build the message
        this.buildmsg()

        # connect if not connected
        if not this.isconnected():
            logger.debug("connection is NOT alive, thus I will reconnect...")
            this.connect()

        # send the mail!
        logger.debug("sending email to {0}".format(recipient))
        try:
            this.connection.sendmail( this.email, recipient, this.msgROOT.as_string())
            logger.debug("email sent successfully!")
            ret = 0
        except smtplib.SMTPRecipientsRefused:
            logger.warning("Problem sending email: SMTPRecipientsREfused")
            ret = 1
        except smtplib.SMTPHeloError:
            logger.warning("Problem sending email: SMTPHeloError")
            ret = 2
        except smtplib.SMTPSenderRefused:
            logger.warning("Problem sending email: SMTPSenderRefused")
            ret = 3
        except smtplib.SMTPDataError:
            logger.warning("Problem sending email: SMTPDataError")
            ret = 4

        return ret

    def add_attachment_image(this, filename):
        this.attachedfiles.append( filename )

    def add_inline_image(this, filename):
        this.inlinefiles.append( filename )

    def add_html(this, html):
        # html = html.encode("utf-8")
        this.htmlbody = '\n'.join( [ this.htmlbody, str(html) ] )

    def finalize_html(this):
        this.htmlbody = '\n'.join( [ "<html><body>",this.htmlbody,"<html><body>" ] )

    def buildmsg(this):
        # metadata
        this.msgROOT["Subject"] = this.subject
        this.msgROOT["From"]    = this.email
        this.msgROOT["To"]      = this.recipient
        this.msgROOT.preamble   = "preamble"


        # finalize the html body
        this.finalize_html()

        # add html to message
        this.msgBODY.attach( MIMEText( this.htmlbody ,'html','utf-8') )

        # add inline images
        for imgfile in this.inlinefiles:
            # open file
            fp = open(imgfile, "rb")
            # read image into a MIMEImage object
            part = MIMEImage(fp.read())
            # close file
            fp.close()
            # add header
            # this give the file an ID to be referenced in the htmlbody for example
            part.add_header('Content-ID', '<{}>'.format(os.path.basename(imgfile)))
            # add this image to the message body
            this.msgBODY.attach( part )

        this.msgROOT.attach( this.msgBODY )


        # add the attached images
        for imgfile in this.attachedfiles:
            # guess type and encoding
            ctype, encoding = mimetypes.guess_type(imgfile)

            # if guessing didn't work out, assume basic octet-stream
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'

            # determine main and subtype
            maintype, subtype = ctype.split('/',1)

            if maintype == "image":
                # open file
                fp = open(imgfile,'rb')
                # a new new image part MIMEBase object
                # read the image into the MIMEBase object
                part = MIMEImage(fp.read(),_subtype=subtype)
                # close file
                fp.close()
            else:
                logger.debug("sending file with maintype {} not supported yet.".format(maintype))

            # encode the image base64
            #Encoders.encode_base64(part)
            # add headers
            # this makes the file a separate ATTACHMENT
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(imgfile))
            # this give the file an ID to be referenced in the htmlbody for example. Optional actually.
            #part.add_header('Content-ID', '<{}>'.format(os.path.basename(imgfile)))
            # add this image to the message itself
            this.msgROOT.attach(part)

    def resetcontent(this):
        this.msgROOT = MIMEMultipart()
        this.msgBODY = MIMEMultipart('related')
        this.subject = ""
        this.recipient = ""
        this.htmlbody = ""
        this.attachedfiles = []
        this.inlinefiles   = []
        

