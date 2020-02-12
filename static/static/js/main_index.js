//自动轮播
$(function () {
    $('#banner .indicator li').click(function () {
        $(this).addClass('active').siblings('.active').removeClass('active');
        var i = $('#banner .indicator li').index(this);
        $($('#banner .inner .item')[i]).addClass('active').siblings('.active').removeClass('active');
    });
    //4个div的统一class = 'div'
    var index = 0;
    //3秒轮播一次
    var timer = setInterval(function () {
        index = (index == 3) ? 0 : index + 1;
        //某个div显示，其他的隐藏
        $("#banner .indicator li").eq(index).addClass('active').siblings('.active').removeClass('active');
        $(".item").hide().eq(index).show();
    }, 3000);
});