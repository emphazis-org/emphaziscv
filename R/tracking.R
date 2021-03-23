#' YOLO back-end for emphazis
#'
#' @description YOLO back-end for `emphazis` tracking functionality.
#'
#' @param video_path Path to video file.
#' @param subject_model Path to model file of folder.
#' @param fps FPS value.
#'
#' @export
proccess_video_yolo <- function(video_path, subject_model, fps) {

  reticulate::source_python(
    file = fs::path_package("emphaziscv", "python", "kalmanFilter.py")
  )

  reticulate::source_python(
    file = fs::path_package("emphaziscv", "python", "tracker.py")
  )


  reticulate::source_python(
    file = fs::path_package("emphaziscv", "python", "tracking.py")
  )

  max_fish <- 1

  result <- reticulate::py$tracking(video_path, max_fish)


  result

  x <- result[1]
  x <- matrix(unlist(x), ncol = max_fish, byrow = FALSE)


  y <- result[2]
  y <- matrix(unlist(y), ncol = max_fish, byrow = FALSE)

  vel <- result[3]
  vel <- matrix(unlist(vel), ncol = max_fish, byrow = FALSE)

  fish_number <- 1

  z <- c()

  for (i in 1:length(x[,fish_number])) {z <- c(z, i)}

  position_table <- tibble::tibble(
    x_center = x[,fish_number],
    y_center = y[,fish_number],
    # speed = vel[,fish_number]
  )

  video_info <- av::av_video_info(video_path)

  fps_video <- round(video_info$video$frames/video_info$duration, 0)

  base::attr(x = position_table, "arena_width") <- video_info$video$width
  base::attr(x = position_table, "arena_height") <- video_info$video$height
  base::attr(x = position_table, "fps") <- fps_video

  return(position_table)
}

# Selecao do codigo python
# reticulate::source_python("data-raw/Python_R/tracking.py")

# reticulate::import_from_path("tracking", path = "data-raw/Python_R/")
# numero de peixes no aquario

# Fun??o que extrai as posicoes X e Y por peixe

# Extracao do valor das posicoes de X de cada peixe

# Extra??o do valor das posicoes de Y de cada peixe

# Extracao do valor das velocidade em pixel de cada peixe

# Qual peixe planeja plotar o grafico de posicao

# Criacao do vetor de frames
# Plotagem da posicao X e Y em relacao ao frame de um peixe

