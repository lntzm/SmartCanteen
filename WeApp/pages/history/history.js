// pages/history-bill/history-bill.js
var util = require('../../utils/util.js')
var touchStartTime = 0;
var touchEndTime = 0;
const DB = wx.cloud.database()
const app = getApp()
Page({
  data: {
    startDate: "",
    endDate: "",
    today: "",
    totalMoney: 0,
    historyBillList: [
    ],
    scrollHeight: "100%",
  },
  //更改开始日期
  startDateChange: function (e) {
    this.setData({
      startDate: e.detail.value
    });
    this.getHistoryBillList();
  },

  //更改结束日期
  endDateChange: function (e) {
    this.setData({
      endDate: e.detail.value
    });
    this.getHistoryBillList();
  },




  onTouchStart: function (e) {
    touchStartTime = e.timeStamp;
  },

  onTouchEnd: function (e) {
    touchEndTime = e.timeStamp;
  },

  //今日账单item点击
  onHisterBillItemClick: function (e) {
    let that = this;
    let billNo = e.currentTarget.dataset.id;
    if (touchEndTime - touchStartTime > 500) {
      wx.showModal({
        title: '提示',
        content: '确认删除本条账单记录！！！',
        success: function (res) {
          if (res.confirm) {
            that.delRecordBill(billNo);
          }
        }
      })
    } else {
      wx.navigateTo({
        url: '../../pages/record-expend/record-expend?billID=' + billNo,
      })
    }
  },

  delRecordBill: function (BillNo) {
    let that = this;
    let openID = wx.getStorageSync('openID');
    let url = app.globalData.address + "/delRecordBill";
    let data = {
      UserNo: openID,
      BillNo: BillNo
    }
    util.HttpGet(url, data, function (res) {
      if (res.Code == 1) {
        that.getTodayBill();
      }
    })
  },

  //请求服务获取历史账单
  getHistoryBillList: function () {
    let that = this;
    let data = {
      StartDate: that.data.startDate,
      EndDate: that.data.endDate,
      PageSize: 20,
      PageIndex: 0,
    }
    var tmp=[]
    var t=0
    var tmp4 = 0
    for(var i=0;i<app.globalData.platesobj.length;i++)
    {
      var str1=''
      var str1=app.globalData.platesobj[i].date
      var st=data.StartDate
      var et=data.EndDate

      console.log(str1)
      console.log(st)
      if(str1>=st && et>=str1)
      {tmp[t]=app.globalData.platesobj[i]
      tmp4 = tmp4 + app.globalData.platesobj[i].price
      t=t+1}
    }
    this.setData({
      historyBillList:tmp,
      totalMoney:tmp4
    })
  },

  onLoad: function (options) {
    // 页面初始化 options为页面跳转所带来的参数

    var startDate = util.addDay(-7);
    this.con().then(res =>{ //请求成功的时候进行下一步流程，这样就可以避免异步问题
      console.log(res)
      
      this.setData({
        startDate: util.formatTime(startDate, "yyyy-MM-dd"),
        endDate: util.formatTime(new Date(), "yyyy-MM-dd"),
        today: util.formatTime(new Date(), "yyyy-MM-dd"),
      });
      
      this.getHistoryBillList();
  　　}).catch(err =>{  //请求失败
  　　　　console.log(err);
        
  　　}); 
    
    
  },
con(){
    let that=this
    return new Promise((reslove, reject)=>{
        DB.collection("plate").where({"user_id":app.globalData.userid,"eaten":"True"}).orderBy('date','desc').get({
        success:res=>{
        console.log(res)
        reslove(res.data, res);
        app.globalData.platesobj=res.data
        },
        fail:err=>{
          reject('请求失败');
        }
        })
    })
  },
  onReady: function () {
   
    // 页面渲染完成

  },
  onShow: function () {
    // 页面显示
   
  },
  onHide: function () {
    // 页面隐藏
  },
  onUnload: function () {
    // 页面关闭
  }
})