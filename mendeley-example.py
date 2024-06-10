from flask import Flask, redirect, render_template, request, session, send_file
import yaml

import zipfile
import os
from io import BytesIO

from mendeley import Mendeley
from mendeley.session import MendeleySession
from datetime import datetime


with open('config.yml') as f:
    config = yaml.safe_load(f)

REDIRECT_URI = 'http://localhost:5000/oauth'

app = Flask(__name__)
app.debug = True
app.secret_key = config['clientSecret']

mendeley = Mendeley(config['clientId'], config['clientSecret'], REDIRECT_URI)


@app.route('/')
def home():
    if 'token' in session:
        return redirect('/listDocuments')

    auth = mendeley.start_authorization_code_flow()
    print(session)
    session['state'] = auth.state
    

    return render_template('home.html', login_url=(auth.get_login_url()))


@app.route('/oauth')
def auth_return():
    auth = mendeley.start_authorization_code_flow(state=session['state'])
    mendeley_session = auth.authenticate(request.url)

    session.clear()
    session['token'] = mendeley_session.token

    return redirect('/listDocuments')


@app.route('/listDocuments')
def list_documents():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    name = mendeley_session.profiles.me.display_name
    docs = mendeley_session.documents.list(view='client').items

    return render_template('library.html', name=name, docs=docs)


@app.route('/document')
def get_document():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    document_id = request.args.get('document_id')
    doc = mendeley_session.documents.get(document_id)

    return render_template('metadata.html', doc=doc)


@app.route('/metadataLookup')
def metadata_lookup():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    doi = request.args.get('doi')
    doc = mendeley_session.catalog.by_identifier(doi=doi)

    return render_template('metadata.html', doc=doc)


@app.route('/download')
def download():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()

    document_id = request.args.get('document_id')
    print(document_id)
    doc = mendeley_session.documents.get(document_id)
    doc_file = doc.files.list().items[0]

    return redirect(doc_file.download_url)


@app.route('/downloadAll')
def download_all():
    if 'token' not in session:
        return redirect('/')

    mendeley_session = get_session_from_cookies()
    docs = mendeley_session.documents.list(view='client').items

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for doc in docs:
            if not doc.files.list().items:
                continue
            print(doc.files.list().items)
            doc_file = doc.files.list().items[0]
            file_content = doc_file.download_url
            zip_file.writestr(f"{doc.title}.pdf", file_content)

    zip_buffer.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(zip_buffer, as_attachment=True, download_name=f'all_documents_{timestamp}.zip')


@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect('/')


def get_session_from_cookies():
    return MendeleySession(mendeley, session['token'])


if __name__ == '__main__':
    app.run()
