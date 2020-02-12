$(function () {
    //请求数据
    $.ajax({
        type: "GET",
        url: baseUrl + "/v1/carts",
        contentType: 'application/json;charset=utf-8',
        dataType: "json",
        beforeSend: function (request) {
            request.setRequestHeader('authorization', window.localStorage.getItem('paopao_token'))
        },
        success: function (response) {
            if (response.code == 200) {
                data = response.data
                initData(data)
                init_view()
            } else {
                alert(response.error)
            }
        },
        error: function (e) {
            console.log(e);
        }
    })

    function init_view() {
        // //所有的商品合计汇总
        var $totalSl = $(".total_r span");
        var $totalZj = $(".total_r b");
        // //一开始就应邀计算一下那个价格的
        // for(var i=0;i<$("#prolist li").length;i++){
        //     $(".pro_zj i").eq(i).html(($(".pro_sl div p").eq(i).html()*$(".pro_jg i").eq(i).html()).toFixed(2));
        // }
        //全选和反选
        var $totalcheck = $(".totalcheck");
        var $procheck = $(".procheck");

        $totalcheck.on("click", function () {
            $procheck.prop("checked", this.checked);
            if (this.checked) {
                $procheck.closest("li").addClass("colorbg");
                //所有的价格和数量都得想加
                totalAll();
            } else {
                $procheck.closest("li").removeClass("colorbg");
                $totalSl.html(0);
                $totalZj.html(0);
            }
        });
        //当点击每一个按钮的时候
        $procheck.on("click", function () {
            if (this.checked) {
                $(this).closest("li").addClass("colorbg");
            } else {
                $(this).closest("li").removeClass("colorbg");
            }
            isAll();
        })
        //当点击批量删除的时候
        $(".pldel").on("click", function (e) {
            e.preventDefault();
            var $procheck = $('.procheck')
            var rel_data = []
            for(var i=$procheck.length-1;i>=0;i--){
                if ($('.procheck').eq(i).prop("checked")==true) {
                    rel_data.push($("#prolist li:eq(" + i + ")").find("p").eq(0).find("i").text())
                    $("#prolist li:eq(" + i + ")").remove()
                }}

               $.ajax({
                type: "delete",
                url: baseUrl + "/v1/carts",
                contentType: "application/json;charset=UTF-8",
                data: JSON.stringify({_method: "delete", 'data': rel_data}),
                dataType: "json",
                beforeSend: function (request) {
                    request.setRequestHeader('authorization', window.localStorage.getItem('paopao_token'))
                },
                success: function (response) {
                        console.log(response)
                    if (response.code == 200) {
                        alert(response.msg)
                    } else {
                        alert(response.error)
                    }
                },
                error: function (e) {
                    console.log(e);
                }
            })



        })
        //当点击每一个删除按钮的时候
        $(".pro_del i").on("click", function () {
            var data = []
            var obj = $(this)
            data.push($(this).closest("li").find("p").eq(0).find("i").text())
            $.ajax({
                type: "delete",
                url: baseUrl + "/v1/carts",
                contentType: "application/json;charset=UTF-8",
                data: JSON.stringify({_method: "delete", 'data': data}),
                dataType: "json",
                beforeSend: function (request) {
                    request.setRequestHeader('authorization', window.localStorage.getItem('paopao_token'))
                },

                success: function (response) {

                    if (response.code == 200) {
                        obj.closest("li").remove();
                        isAll();
                        // console.log($(this).closest("li").find("input")[0].checked);
                        if ($("#prolist li").length == 0) {
                            $(".totalcheck").prop("checked", false);
                        }
                        alert(response.msg)
                    } else {
                        alert(response.error)
                    }
                },
                error: function (e) {
                    console.log(e);
                }
            })
        });
        //点击左右的增加或者减少的按钮
        $(".pro_sl div span").on("click", function (e) {
            e.preventDefault();
            var $proNum = Number($(this).siblings("p").html());
            if ($(this).hasClass("pro_sl_j")) {
                $proNum--;
                if ($proNum < 1) {
                    return;
                }
                $(this).siblings("p").html($proNum);
            } else if ($(this).hasClass("pro_sl_s")) {
                $proNum++;
                $(this).siblings("p").html($proNum);
            }
            $(this).closest("li").find(".pro_zj i").html(($proNum * $(this).closest("li").find(".pro_jg i").html()).toFixed(2));
            isAll();
        })

        $("#pay_button").on("click", function (e) {
            if (parseInt($totalSl.text() <= 0) || (parseFloat($totalZj.text()) <= 0)) {
                alert('请先选择要购买的股票。')
                return
            }
            var $procheck = $('.procheck')
            var rel_data = ''
            for(var i=$procheck.length-1;i>=0;i--){
                if ($('.procheck').eq(i).prop("checked")==true) {
                    rel_data+= $("#prolist li:eq(" + i + ")").find("p").eq(0).find("i").text()+','
                }}
            datas={}
            datas.id = rel_data.substring(0, rel_data.lastIndexOf(','))
            datas.price = $totalZj.text()
            datas.type=1
            create_order(datas)
        })

    }


    //定义一个判断的的函数
    function isAll() {
        //已经点击的长度
        var $totalcheck = $(".totalcheck");
        var $checkedLen = $("#prolist li :checked").length;
        var $checkAlllen = $("#prolist li").length;
        if ($checkedLen == $checkAlllen) {
            $totalcheck.prop("checked", true);
            totalAll();
        } else {
            $totalcheck.prop("checked", false);
            //这里需要判断下有多少选中的，将选中的价格和数量加起来
            choiceLi($checkedLen);
        }
    }

    //封装一个价格和数量汇总的函数
    function totalAll() {
        var $totalSl = $(".total_r span");
        var $totalZj = $(".total_r b");
        var $proZj = $(".pro_zj i");
        var $proSl = $(".pro_sl p");
        var $totalNum = 0;
        var $totalPrice = 0;
        var $Len = $("#prolist li").length;
        for (var i = 0; i < $Len; i++) {
            $totalNum += Number($proSl.eq(i).html());
            $totalPrice += Number($proZj.eq(i).html());
        }
        $totalSl.html($totalNum);
        $totalZj.html($totalPrice.toFixed(2));
    }

    //封装一个选中的
    function choiceLi(len) {
        var $totalSl = $(".total_r span");
        var $totalZj = $(".total_r b");
        var $totalNum = 0;
        var $totalPrice = 0;
        var $choiceP = $("#prolist li :checked").closest("li").find(".pro_sl div p");
        var $choiceI = $("#prolist li :checked").closest("li").find(".pro_zj i");
        //选中的是多少个
        for (var i = 0; i < len; i++) {
            $totalNum += Number($choiceP.eq(i).html());
            $totalPrice += Number($choiceI.eq(i).html());
        }
        $totalSl.html($totalNum);
        $totalZj.html($totalPrice.toFixed(2));
    }

})


function initData(data) {
    for (var i = 0; i < data.length; i++) {
        obj = data[i]
        html = '<li>' +
            '                <div class="pro_tit" style="width:21%;">' +
            '                    <div>' +
            '                        <input type="checkbox" class="procheck">' +
            '                    </div>' +
            '                    <dl>' +
            '                        <dd>' +
            '                            <a href="#">' + obj.stock_name + '</a>' +
            '                        </dd>' +
            '                    </dl>' +
            '                </div>' +
            '                <p class="pro_hh" style="width:17%;"><i>' + obj.stock_id + '</i></p>' +
            '                <div class="pro_jg" style="width:13%;">' +
            '                    <i>' + parseFloat(obj.stock_price) + '</i>' +
            '                </div>' +
            '                <div class="pro_sl" style="width:17%;">' +
            '                    <div>' +
            '                        <span class="pro_sl_j">-</span>' +
            '                        <p>' + parseInt(obj.stock_count) + '</p>' +
            '                        <span class="pro_sl_s">+</span>' +
            '                    </div> ' +
            '                </div>' +
            '                <div class="pro_zj" style="width:17%;">' +
            '                    <i>' + parseInt(obj.stock_count) * parseFloat(obj.stock_price) + '</i>' +
            '                </div>' +
            '                <div class="pro_del" style="width:10%;">' +
            '                    <i class="layui-icon">删除</i>' +
            '                </div>' +
            '            </li>'

        $("#prolist").append(html)
    }

}


function create_order(datas) {
        console.log(datas)
        $.ajax({
            type: "POST",
            url: baseUrl + "/v1/financing/order",
            contentType: 'application/json;charset=utf-8',
            data: JSON.stringify(datas),
            dataType: "json",
            beforeSend: function (request) {
                request.setRequestHeader('authorization', window.localStorage.getItem('paopao_token'))
            },
            success: function (response) {
                if (response.code == 200) {
                    pay_carts(response.data.order_id,response.data.order_price)
                } else {
                    alert(response.error)
                }

            },
            error: function (e) {
                alert(e)
            }
        });
    }
    function pay_carts(order_id, price) {

        var post_data = {"trade_no": order_id, 'amount_price': price,'return_url':'static/templates/funds.html'}
        $.ajax({
            url: baseUrl + '/v1/payment/jump',
            type: 'post',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(post_data), beforeSend: function (request) {
                request.setRequestHeader('authorization', window.localStorage.getItem('paopao_token'))
            },
            success: function (data) {
                //获取支付宝跳转地址
                window.location.href = data.pay_url
            }
        })

    }