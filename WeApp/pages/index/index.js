// index.js
// 获取应用实例
const app = getApp()
var util = require('../../utils/util.js')
var touchStartTime = 0;
var touchEndTime = 0;
const DB = wx.cloud.database()
Page({
  data:{
    userInfo: {},
    hasUserInfo: false,
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    canIUseGetUserProfile: false,
    canIUseOpenData: wx.canIUse('open-data.type.userAvatarUrl') && wx.canIUse('open-data.type.userNickName'), // 如需尝试获取用户信息可改为false
    //判断小程序的API，回调，参数，组件等是否在当前版本可用。
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    isHide: true,
    albumDisabled: true,
    bindDisabled: false,
    userid:0,
    dataobj:{},
    canteenobj:{},
    platesobj:[{},{},{}],
    platesobj_today:[],
    plateobj:{},
    food:[],
    calories:0,
    remain:0,
    openId:"xxx",
    weekday:2,
    gender:0,
    fat:0,
    protein:0,
    carbo:0,
    today_money:0,
    recommend_calories:0,
    recommend_fat:0,
    recommend_protein:0,
    recommend_carbo:0,
    user_money:0
  },
onLoad: function(options) {
    if (wx.getUserProfile) {
      this.setData({
        canIUseGetUserProfile: true
      })
    }
    this.clickinfo()
    app.checkLoginReadyCallback = res => {
      this.setData({
        openId:app.globalData.openid
      })
    };
    var that = this;
    // 查看是否授权
    wx.getSetting({
        success: function(res){
            if (res.authSetting['scope.userInfo']) {
                wx.getUserInfo({
                    success: function(res) {
                        wx.login({
                            success: res => {
                                //console.log("用户的code:" + res.code);

                            }
                        });
                    }
                });
            } else {
                // 用户没有授权
                // 改变 isHide 的值，显示授权页面
                that.setData({
                    isHide: true
                });
            }
        }
    });

    DB.collection("canteen").where({"weekday":app.globalData.weekday}).get({
      success:res=>{
        that.setData({
          canteenobj:res.data[0]
      })
    }
    })
    DB.collection("canteen").get({
      success:res=>{
        app.globalData.canteenobj=res.data
      }
    })
    
    this.con2().then(res =>{ //请求成功的时候进行下一步流程，这样就可以避免异步问题
      var tmp=0
      var tmp2=0
      var fat=0,protein=0,carbo=0,money=0
      app.globalData.platesobj=this.data.platesobj
      app.globalData.userid=this.data.dataobj.id
      app.globalData.canteenobj2=this.data.canteenobj
      if (this.data.platesobj.length==0)
      console.log("今日未消费");
      for(var i=0;i<this.data.platesobj.length;i++)
            { 
              var tmp3=0
              /*for(var j=0;j<this.data.canteenobj.food.length;j++)
              {
              var x=0
              console.log(app.globalData.today)
                  if(this.data.platesobj[i].food==this.data.canteenobj.food[j])
                  {x=1*(parseInt(this.data.canteenobj.weight[j])-parseInt(this.data.platesobj[i].rest))
                  tmp2 = tmp2 + parseInt(this.data.canteenobj.calories[j])*x/100
                  tmp3 = tmp3 + x}
              }*/
              var consume=0,calories=0,rest=0
              consume=this.data.platesobj[i].weight - this.data.platesobj[i].rest_weight
              calories=this.data.platesobj[i].calories
              rest = this.data.platesobj[i].rest_weight
              tmp = tmp + rest
              tmp2 = tmp2 + calories*consume/100
              fat = fat + this.data.platesobj[i].fat*consume/100
              protein = protein + this.data.platesobj[i].protein*consume/100
              carbo = carbo + this.data.platesobj[i].carbo*consume/100
              money = money + this.data.platesobj[i].price
            }
            var user_weight,user_height,user_age,tmp5,tmp6,tmp7,tmp8,money1
            money1 = this.data.dataobj.money
            user_weight = this.data.dataobj.weight
            user_height = this.data.dataobj.height
            user_age = this.data.dataobj.age
            tmp5 = (67 + 13.73*user_weight + 5*user_height - 6.9*user_age) * 1.2
            tmp6 = 0.45 * user_weight
            tmp7 = 0.8 * user_weight
            tmp8 = tmp5 / 8
            this.setData({
                remain:parseInt(tmp),
                calories:parseInt(tmp2),
                fat:parseInt(fat),
                protein:parseInt(protein),
                carbo:parseInt(carbo),
                user_money:money1.toFixed(2),
                today_money:money.toFixed(2),
                recommend_calories:parseInt(tmp5),
                recommend_fat:parseInt(tmp6),
                recommend_protein:parseInt(tmp7),
                recommend_carbo:parseInt(tmp8),
            })
          console.log(res);
      　　}).catch(err =>{  //请求失败
      　　　　console.log(err);
      　　});
    
    app.checkLoginReadyCallback = res => {
    this.setData({
      dataobj:app.globalData.userobj
    })
  };
    
},
con(){
  let that=this
  return new Promise((reslove, reject)=>{
    DB.collection("testlist").where({"_openid": this.data.openId }).get({
      success:res=>{
      if(res.data.length===0)
      {
        this.addData_New(this.data.openId);
      }
      else
      {reslove(res.data, res);
        that.setData({
        dataobj:res.data[0],
        gender:res.data[0].gender
      })}
        
      },
      fail:res=>{
        reject('请求失败');
      }
    })
    
  })
},
con2(){
  let that=this
  return new Promise((reslove, reject)=>{
    this.con().then(res =>{ //请求成功的时候进行下一步流程，这样就可以避免异步问题
      console.log(app.globalData.today)
      DB.collection("plate").where({"user_id":this.data.dataobj.id,"date":app.globalData.today,"eaten":"True"}).get({
      success:res=>{
      console.log(res)
      reslove(res.data, res);
      this.setData({
        platesobj:res.data
      })
      }
      })
      
  　　}).catch(err =>{  //请求失败
  　　　　console.log(err);
        reject('请求失败');
  　　}); 
  })
},
bindGetUserInfo: function(e) {
    if (e.detail.userInfo) {
        //用户按了允许授权按钮
        var that = this;
        // 获取到用户的信息了，打印到控制台上看下
        console.log("用户的信息如下：");
        console.log(e.detail.userInfo);
        //授权成功后,通过改变 isHide 的值，让实现页面显示出来，把授权页面隐藏起来
        that.setData({
            isHide: false,
            userInfo:e.detail.userInfo
        });
    } else {
        //用户按了拒绝按钮
        wx.showModal({
            title: '警告',
            content: '您点击了拒绝授权，将无法进入小程序，请授权之后再进入!!!',
            showCancel: false,
            confirmText: '返回授权',
            success: function(res) {
                // 用户没有授权成功，不需要改变 isHide 的值
                if (res.confirm) {
                    console.log('用户点击了“返回授权”');
                }
            }
        });
    }
},
addData(){
    console.log('调用添加数据的方法')
    DB.collection("testlist").add({
      data:{
        nickname:'张三',
        id:"2021",
        weight:70,
        age:25,
        height:180,
        gender:2//male for 1,famale for 2
      },
      success(res) {
        console.log("成功", res)
      }, 
      fail(res) {
        console.log("失败", res)
      }
    })
  },
getUserProfile(e) {
    // 推荐使用wx.getUserProfile获取用户信息，开发者每次通过该接口获取用户个人信息均需用户确认，开发者妥善保管用户快速填写的头像昵称，避免重复弹窗
    wx.getUserProfile({
      desc: '展示用户信息', // 声明获取用户个人信息后的用途，后续会展示在弹窗中，请谨慎填写
      success: (res) => {
        console.log(res)
        this.setData({
          userInfo: res.userInfo,
          hasUserInfo: true
        })
      }
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
        gender:0,//male for 1,famale for 2
        money:0,
        food:new Array()
      },
      success(res) {
        console.log("成功", res)
      }, 
      fail(res) {
        console.log("失败", res)
      }
    })
  },
  getUserInfo(e) {
    // 不推荐使用getUserInfo获取用户信息，预计自2021年4月13日起，getUserInfo将不再弹出弹窗，并直接返回匿名的用户个人信息
    console.log(e)
    this.setData({
      userInfo: e.detail.userInfo,
      hasUserInfo: true
    })
    this.globalData.userinfo=userInfo;
  },
  checkboxChange(e) {
    console.log('checkbox发生change事件，携带value值为：', e.detail.value)

    const items = this.data.items
    const values = e.detail.value
    for (let i = 0, lenI = items.length; i < lenI; ++i) {
      items[i].checked = false

      for (let j = 0, lenJ = values.length; j < lenJ; ++j) {
        if (items[i].value === values[j]) {
          items[i].checked = true
          break
        }
      }
    }

    this.setData({
      items
    })
  },
  clickinfo(){
    let that = this ;
   wx.showModal({
          title: '温馨提示',
          content: '服务号想要向您发送消息',
          confirmText:"同意",
          cancelText:"拒绝",
          success: function (res) {
              if (res.confirm) {
                 //调用订阅消息
                 wx.requestSubscribeMessage({
                  tmplIds: ['O9oo_L0ID37aV0MXYbct3F3HwrygCJXta2THrbnQUes','4HskV0UGpaaPqojLHWqCl3m-8Ktvy6nPLVIv3MQoG2M'],
                  success (res) { 
                    console.log(res)
                  },
                  fail (err)
                  {
                    console.log(err)
                  }
                }),
                  console.log('未更新时长大于7天，可能看到的是旧食谱');
                  //调用订阅

              } else if (res.cancel) {
                  console.log('用户点击取消');
                  ///显示第二个弹说明一下
                  wx.showModal({
                    title: '温馨提示',
                    content: '拒绝后您将无法获取实时的与卖家（买家）的交易消息',
                    confirmText:"知道了",
                    showCancel:false,
                    success: function (res) {
                      ///点击知道了的后续操作 
                      ///如跳转首页面 
                    }
                });
              }
          }
      });

  }
})