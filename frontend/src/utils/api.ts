import axios from 'axios'

const DEFAULT_ERROR_MESSAGE = 'Có lỗi xảy ra. Vui lòng thử lại.'

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return DEFAULT_ERROR_MESSAGE
  }

  const status = error.response?.status
  const responseMessage = (error.response?.data as { message?: string } | undefined)?.message

  if (responseMessage) {
    return responseMessage
  }

  switch (status) {
    case 400:
      return 'Yêu cầu không hợp lệ. Vui lòng kiểm tra lại các trường.'
    case 401:
      return 'Bạn chưa được xác thực. Vui lòng đăng nhập lại.'
    case 403:
      return 'Bạn không có quyền truy cập. Vui lòng liên hệ quản trị viên.'
    case 409:
      return 'Dữ liệu đã tồn tại hoặc xung đột. Vui lòng thử lại với thông tin khác.'
    case 500:
      return 'Lỗi máy chủ. Vui lòng thử lại sau ít phút.'
    default:
      return error.message || DEFAULT_ERROR_MESSAGE
  }
}
