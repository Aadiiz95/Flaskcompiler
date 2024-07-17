from flask import Flask, request, send_from_directory, jsonify
import subprocess
import os
import tempfile

app = Flask(__name__, static_folder=None)

@app.route("/codemirror-5.65.16/<path:path>")
def send_codemirror(path):
    return send_from_directory("C:/my_flask_app/codemirror-5.65.16", path)

@app.route("/")
def index():
    # Simulate compiler.flush() equivalent
    temp_dir = tempfile.gettempdir()
    for f in os.listdir(temp_dir):
        try:
            os.remove(os.path.join(temp_dir, f))
        except Exception as e:
            print(f"Error deleting file: {e}")
    print("deleted")
    return send_from_directory("C:/my_flask_app", "index.html")

@app.route("/compile", methods=["POST"])
def compile_code():
    code = request.json.get("code")
    input_data = request.json.get("input")
    lang = request.json.get("lang")
    env_data = {"OS": "windows"}

    try:
        if lang == "Cpp":
            result = compile_cpp(code, input_data)
        elif lang == "Java":
            result = compile_java(code, input_data)
        elif lang == "Python":
            result = compile_python(code, input_data)
        else:
            result = {"output": "Unsupported language"}

        return jsonify(result)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"output": "error"}), 500

def compile_cpp(code, input_data):
    with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False) as src_file:
        src_file.write(code.encode())
        src_file.flush()
        src_file.close()
        exec_file = src_file.name[:-4]

        if input_data:
            return compile_with_input(src_file.name, exec_file, input_data, "g++", "./a.out")
        else:
            return compile_without_input(src_file.name, exec_file, "g++", "./a.out")

def compile_java(code, input_data):
    with tempfile.NamedTemporaryFile(suffix=".java", delete=False) as src_file:
        src_file.write(code.encode())
        src_file.flush()
        src_file.close()
        exec_file = src_file.name[:-5]

        if input_data:
            return compile_with_input(src_file.name, exec_file, input_data, "javac", "java")
        else:
            return compile_without_input(src_file.name, exec_file, "javac", "java")

def compile_python(code, input_data):
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as src_file:
        src_file.write(code.encode())
        src_file.flush()
        src_file.close()

        if input_data:
            return compile_with_input(src_file.name, None, input_data, "python", "python")
        else:
            return compile_without_input(src_file.name, None, "python", "python")

def compile_without_input(src_file, exec_file, compile_cmd, run_cmd):
    try:
        compile_cmd = [compile_cmd, src_file]
        print(f"Compile command: {' '.join(compile_cmd)}")
        subprocess.run(compile_cmd, check=True, timeout=50)  # Increased timeout to 50 seconds
        if exec_file:
            run_cmd = [exec_file]
        else:
            run_cmd = [run_cmd, src_file]
        print(f"Run command: {' '.join(run_cmd)}")
        result = subprocess.run(run_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=50)  # Increased timeout to 50 seconds
        return {"output": result.stdout.decode()}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr.decode()}
    except subprocess.TimeoutExpired:
        return {"output": "timeout"}

def compile_with_input(src_file, exec_file, input_data, compile_cmd, run_cmd):
    try:
        compile_cmd = [compile_cmd, src_file]
        print(f"Compile command: {' '.join(compile_cmd)}")
        subprocess.run(compile_cmd, check=True, timeout=50)  # Increased timeout to 50 seconds
        if exec_file:
            run_cmd = [exec_file]
        else:
            run_cmd = [run_cmd, src_file]
        print(f"Run command: {' '.join(run_cmd)} with input")
        result = subprocess.run(run_cmd, input=input_data.encode(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=50)  # Increased timeout to 50 seconds
        return {"output": result.stdout.decode()}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr.decode()}
    except subprocess.TimeoutExpired:
        return {"output": "timeout"}

