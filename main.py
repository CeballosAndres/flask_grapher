import os
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './files'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
PORT = 5000
DEBUG = True
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = 'c\xbb\xce>m\xe6(sn:\x19\xe6w\xa0K\x90EI\xbd3\x815Fm'
plt.switch_backend('Agg')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

@app.route('/', methods=['GET'])
def index():
    return render_template('grapher/load_file.html')

@app.route('/us', methods=['GET'])
def us():
    return render_template('about/us.html')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part','warning')
            return redirect(request.url)
        # recibir el archivo 
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file','warning')
            return redirect(request.url)
        # revisar que sea del tipo csv
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #De serlo, ir a la nueva pagina una vez subido
            flash('Archivo almacenado con éxito.', 'success')
            return redirect(url_for('uploaded', filename=filename))
        else:
            #Sino, seguir en la misma pagina, agregar el mensaje de errors
            flash('Tipo de archivo incorrecto, seleccione otro archivo.', 'warning')
    return redirect(url_for('index'))

@app.route('/uploaded/<string:filename>', methods=['GET', 'POST'])
def uploaded(filename):
    graphs = ['Barras','Pastel']
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(file)
    options = df.select_dtypes(include=numerics).columns.format()

    if request.method == 'POST':
        graph_column = request.form['graph-column']
        graph_type = request.form['graph-type']
        graph_title = request.form['graph-title']
        serie = df[graph_column]
        graph_file_name = "{}.png".format(graph_title)
        plt.bar(serie.index,serie,color='red')
        plt.title(graph_title)
        plt.savefig(os.path.join('./static/graphs', graph_file_name))
        return redirect(url_for('grapher', filename=filename, graph=graph_file_name))

    return render_template('grapher/uploaded_file.html', options=options, graphs=graphs)

@app.route('/grapher/<string:filename>/<string:graph>', methods=['GET'])
def grapher(filename, graph):
    graph_path = os.path.join('graphs', graph)
    return render_template('grapher/grapher.html', image=graph_path, filename=filename)

if __name__ == '__main__':
    app.run(port=PORT, debug=DEBUG)
