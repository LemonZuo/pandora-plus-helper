import dayjs from "dayjs";
import 'dayjs/locale/zh-cn';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';

dayjs.locale('zh-cn');
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(customParseFormat);

dayjs.extend(timezone);
dayjs.extend(customParseFormat);

const formatDateTime = (dateTimeStr: string | number | Date): string => {
  // 使用 dayjs 与 timezone 插件进行日期转换，这里指定 'Asia/Shanghai' 为时区
  const date = dayjs(dateTimeStr, 'YYYY-MM-DD HH:mm:ss').tz('Asia/Shanghai');

  // 检查日期是否有效并进行格式化，同时包括时区信息
  if (date.isValid()) {
    return date.format('YYYY-MM-DD HH:mm:ss');
  } else {
    console.error('Invalid date:', dateTimeStr);
    return 'Invalid date';
  }
}

export default formatDateTime;
