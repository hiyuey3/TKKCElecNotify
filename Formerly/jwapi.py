from flask import Blueprint, request, jsonify
import JwUtil
jw_baseUrl="http://jw.xujc.com/"
# eapi_bp = Blueprint('eapi' , __name__,url_prefix="/api/e")
jwapi_bp = Blueprint('jwapi' , __name__,url_prefix="/api/jw")

jwapi_bp.route('/getCaptcha',methods=['GET'])
def getCaptcha():
    captcha_url = jw_baseUrl+'imginfo.php'


