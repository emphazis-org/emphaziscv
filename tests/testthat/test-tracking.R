testthat::test_that("yolov4 3s", {
  video_path <- fs::path_package("emphaziscv", "extdata", "video_3s.mp4")
  subject_num <- 1

  position_table <- proccess_video_yolo(
    video_path = video_path,
    subject_model = NULL,
    fps = 3
  )

  # fig <- plotly::plot_ly(
  #   data = position_table,
  #   x = ~x,
  #   y = ~y,
  #   z = ~z,
  #   type = 'scatter3d',
  #   mode = 'lines',
  #   opacity = 1,
  #   line = list(width = 6, reverscale = FALSE)
  # )
  # fig

  testthat::expect_equal(ncol(position_table), 3)
})


testthat::test_that("yolov4 20s", {

  video_path <- fs::path_package("emphaziscv", "extdata", "video_20s.mp4")
  subject_num <- 1

  tictoc::tic("start 20s video")
  position_table <- proccess_video_yolo(
    video_path = video_path,
    subject_model = NULL
  )
  tictoc::toc()

})

1049/20
