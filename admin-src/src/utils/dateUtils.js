import dayjs from 'dayjs'
import isBetween from 'dayjs/plugin/isBetween'
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore'
import isSameOrAfter from 'dayjs/plugin/isSameOrAfter'

dayjs.extend(isBetween)
dayjs.extend(isSameOrBefore)
dayjs.extend(isSameOrAfter)

export const formatDate = (date) => date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-'
export const isInPeriod = (start, end) => dayjs().isBetween(dayjs(start), dayjs(end))
export const formatTimeOnly = (date) => date ? dayjs(date).format('HH:mm:ss') : '-'
export const formatDateTime = (date) => date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
export default dayjs 