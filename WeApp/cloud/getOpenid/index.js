// 云函数入口文件
const cloud = require('wx-server-sdk')
cloud.init({
  env: 'mydatabase1-4glgbmlu103a6c74'
})
exports.main = async (event, context) => {
  const wxContext = cloud.getWXContext()

  return {
    event,
    openid: wxContext.OPENID,
    appid: wxContext.APPID,
    unionid: wxContext.UNIONID,
  }
}
