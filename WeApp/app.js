// app.js
const that1 = this
var util = require('utils/util.js')
var that
App({
  globalData:{
    openid:"1",
    userInfo: null,
    userobj:{},
    gender:0,
    weekday_check:0,
    canteenobj:[],
    canteenobj2:[],
    platesobj:[],
    platesobj_today:[],
    today:util.formatTime(new Date(), "yyyy-MM-dd"),
    weekday:util.formatTime(new Date(), "week"),
    userid:""
  },
  onLaunch:function() {
    // 展示本地存储能力
    that=this
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    //云开发环境初始化
    wx.cloud.init({
      env:"mydatabase1-4glgbmlu103a6c74",
      traceUser:true
    })
    that.getOpenid()
    
    // 登录
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
      }
    })
  },
getOpenid() {
  var that1 = this;
  wx.cloud.callFunction({
    name: 'getOpenid',
    complete: res => {
      //console.log('openid: ', res.result.openid)
      //console.log('appid: ', res.result.appid)
      let OPENID = res.result.openid
      that1.globalData.openid=OPENID
      if(this.checkLoginReadyCallback)
      this.checkLoginReadyCallback(res);
    }
  })
},
getuserobj()
{
  DB.collection("testlist").where({"_openid": this.globalData.openid }).get({
    success:res=>{
    console.log(res)
    if(res.data.length===0)
    {
      console.log("用户不存在")
      //this.addData_New(this.data.openId);
    }
    else
    {console.log("用户存在")
      this.globalData.userobj=res.data[0]
      this.globalData.gender=res.data[0].gender
      if(this.checkLoginReadyCallback2)
      this.checkLoginReadyCallback2(res);
      }
      
    },
    fail:res=>{
      console.log("失败")
    }
  })
}
})