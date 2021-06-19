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
    gender:0,
    input_nickname:"",
    input_age:0,
    input_gender:0,
    input_height:0,
    input_weight:0,
    items: [
    {
      name: '保密',
      value: 0,
      show:true,
    },
    {
      name: '男',
      value: 1,
      show:true,
    },
    {
      name: '女',
      value: 2,
      show:true,
    }]
    },
 
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var getAppInfo = app.globalData.openid;
    var that = this;
    this.setData({
      openid:getAppInfo
    })
    DB.collection("testlist").where({"_openid": this.data.openid }).get({
      success:res=>{
       // console.log(res)
      {that.setData({
        dataobj:res.data[0],
        gender:res.data[0].gender,
        input_nickname:res.data[0].nickname,
        input_age:res.data[0].age,
        input_gender:res.data[0].gender,
        input_height:res.data[0].height,
        input_weight:res.data[0].weight
      })
      }
        
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
  radioChange(e) {
    var items = this.data.items;
    var currentItemName = e.detail.value;
    var that = this;
    for (var i = 0; i < items.length; i++) {
    if (currentItemName.indexOf(items[i].value) != -1) {
        items[i].checked = true;
        that.setData({
          input_gender:i
        })
    } else {
        items[i].checked = false;
    }
}
this.setData({
    items: items
})
  },
  bindKeyInput_nickname: function (e) {
    this.setData({
      input_nickname: e.detail.value
    })
  },
  bindKeyInput_age: function (e) {
    this.setData({
      input_age: parseInt(e.detail.value)
    })
  },
  bindKeyInput_height: function (e) {
    this.setData({
      input_height: parseInt(e.detail.value)
    })
  },
  bindKeyInput_weight: function (e) {
    this.setData({
      input_weight: parseInt(e.detail.value)
    })
  },
  change_info:function(e)
  {
    console.log('调用修改更新数据的方法')
    DB.collection("testlist").doc(this.data.dataobj._id).update({
      data: {
        "nickname": this.data.input_nickname,
        "age":this.data.input_age,
        "weight":this.data.input_weight,
        "height":this.data.input_height,
        "gender":this.data.input_gender
      },
      success(res) {
        console.log('修改更新数据成功', res.data)
      },
      fail(res) {
        console.log("修改更新数据失败", res)
      }
    })

  },
  goto_userinfo:function()
  {
    wx.navigateTo({
      url: '/pages/mine/mine',
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