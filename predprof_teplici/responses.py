from flask import make_response, jsonify

def SuccessResponse(result):
    response_data = {"ok":True, "result":result}
    
    response = make_response(jsonify(response_data))
    
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers["Content-Type"] = "application/json"
    
    return response

#{
#   ok: false,
#   error_code: error_code,
#   description: "wewewe"
#}
def ErrorResponse(description, error_code):
    response_data = {"ok":False, "error_code":error_code, "description":description}

    response = make_response(jsonify(response_data), error_code)

    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers["Content-Type"] = "application/json"

    return response
