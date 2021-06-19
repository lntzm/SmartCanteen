// pages/shipu/shipu.js
const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    listData:[
      {"code":"周一","text":"text1","type":"type1"},
      {"code":"周二","text":"text2","type":"type2"},
      {"code":"周三","text":"text3","type":"type3"},
      {"code":"周四","text":"text4","type":"type4"},
      {"code":"周五","text":"text5","type":"type5"},
      {"code":"周六","text":"text6","type":"type6"},
      {"code":"周日","text":"text7","type":"type7"}
      ]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

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

  },
jump1:function(){
  app.globalData.weekday_check=1
  wx.navigateTo({
    url: '/pages/shipu_detail/shipu_detail',
    })
},
jump2:function(){
  app.globalData.weekday_check=2
  wx.navigateTo({
    url: '/pages/shipu_detail/shipu_detail',
    })
},
jump3:function(){
  app.globalData.weekday_check=3
  wx.navigateTo({
    url: '/pages/shipu_detail/shipu_detail',
    })
},
jump4:function(){
  app.globalData.weekday_check=4
  wx.navigateTo({
    url: '/pages/shipu_detail/shipu_detail',
    })
},
jump5:function(){
  app.globalData.weekday_check=5
  wx.navigateTo({
    url: '/pages/shipu_detail/shipu_detail',
    })
},
jump6:function(){
  app.globalData.weekday_check=6
  wx.navigateTo({
    url: '/pages/shipu_detail/shipu_detail',
    })
},
jump7:function(){
  app.globalData.weekday_check=7
  wx.navigateTo({
    url: '/pages/shipu_detail/shipu_detail',
    })
}

})
