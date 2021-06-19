// pages/userinfo/userinfo.js
const DB = wx.cloud.database()
const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    dataobj:{},
    openid:"xxx",
    gender:0
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    var getAppInfo = app.globalData.openid;
    var that = this;
    this.setData({
      openid:getAppInfo
    })
    console.log(getAppInfo)
    DB.collection("testlist").where({"_openid": this.data.openid }).get({
      success:res=>{
       // console.log(res)
      that.setData({
        dataobj:res.data[0],
        gender:res.data[0].gender
      })
        
      }
    })
  },

  goto_change_userinfo:function()
  {
    wx.navigateTo({
      url: '/pages/change_userinfo/change_userinfo',
      })
  },
  addData_New(new_id){
    console.log('调用添加数据的方法1')
    DB.collection("testlist").add({
      data:{
        nickname:"未设置",
        id:new_id,
        weight:0,
        age:0,
        height:0,
        gender:0//male for 1,famale for 2
      },
      success(res) {
        console.log("成功", res)
      }, 
      fail(res) {
        console.log("失败", res)
      }
    })
  },
  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  }
})