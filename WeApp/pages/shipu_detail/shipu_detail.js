// pages/shipu_detail/shipu_detail.js
const app = getApp()
const DB = wx.cloud.database()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    weekday:2,
    canteenobj:{},
    datalist:[
      {name:"",calories:""},
      {name:"",calories:""},
      {name:"",calories:""},
      {name:"",calories:""},
      {name:"",calories:""},
      {name:"",calories:""},
      {name:"",calories:""},
      {name:"",calories:""},
      {name:"",calories:""}
    ]
  },
  sleep:function(time) {
    var startTime = new Date().getTime() + parseInt(time, 10);
    while(new Date().getTime() < startTime) {}
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    this.setData({
      weekday:app.globalData.weekday_check
    })
    var tmp =this.data.datalist
    this.data.canteenobj=app.globalData.canteenobj[this.data.weekday-1]
    console.log(this.data.canteenobj)
    for(var i=0;i<this.data.canteenobj.food.length;i++)
    {
      tmp[i].name=this.data.canteenobj.food[i]
      tmp[i].calories=this.data.canteenobj.calories[i]
    }
    this.setData({
        datalist:tmp
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

  },
  
})