"""
人脸API调用的相关参数设置
"""

"""人脸检测部分"""
det_options = {}
det_options["face_field"] = "beauty,quality"    # 返回颜值 人脸质量
det_options["max_face_num"] = 1                 # 人脸检测数
det_options["face_type"] = "LIVE"               # 相机拍摄风格
det_options["liveness_control"] = "LOW"         # 活体检测

"""人脸注册部分"""
register_options = {}
register_options["user_info"] = "user's info"       # 用户信息  
register_options["quality_control"] = "NORMAL"      # 人脸质量控制
register_options["liveness_control"] = "LOW"        # 活体检测
register_options["action_type"] = "APPEND"          # 已注册 则在该用户尾部追加新的人脸

"""人脸搜索部分"""
search_options = {}