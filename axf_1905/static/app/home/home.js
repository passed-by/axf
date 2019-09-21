$(function () {

    // 顶部轮播
    new Swiper('#topSwiper .swiper-container', {
        loop: true,
        pagination: '.swiper-pagination'  //分页器
    });

    // 必购的轮播
    new Swiper('#swiperMenu .swiper-container', {
         slidesPerView: 3
    });

});
