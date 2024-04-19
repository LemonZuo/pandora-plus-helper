import apiClient from '../apiClient';

import {Token} from '#/entity';

export enum TokenApi {
  list = '/token/list',
  add = '/token/add',
  update = '/token/update',
  delete = '/token/delete',
  refresh = '/token/refresh',
  search = '/token/search',
  startTask = '/token/start',
  stopTask = '/token/stop',
  statusTask = '/token/task_status',
}

const getTokenList = () => apiClient.get<Token[]>({ url: TokenApi.list }).then((res) => {
  // 将shareList转为json对象
  // res.forEach((item) => {
  //   if (item.shareList) {
  //     item.shareList = JSON.parse(item.shareList);
  //   }
  // });
  return res;
});

const searchTokenList = (tokenName: string) => apiClient.post<Token[]>({ url: TokenApi.search, data: {tokenName} }).then((res) => {
  // 将shareList转为json对象
  // res.forEach((item) => {
  //   if (item.shareList) {
  //     item.shareList = JSON.parse(item.shareList);
  //   }
  // });
  return res;
});
export interface TokenAddReq {
  id?: number;
  tokenName: string;
  refreshToken: string;
}
export interface taskStatus {
  status: boolean;
}
const addToken = (data: TokenAddReq) => apiClient.post({ url: TokenApi.add, data });
const updateToken = (data: TokenAddReq) => apiClient.post({ url: TokenApi.update, data });
const deleteToken = (id: number) => apiClient.post({ url: TokenApi.delete, data: { id } });
const refreshToken = (id: number) => apiClient.post({ url: TokenApi.refresh, data: { id } })
const startTask = () => apiClient.post({ url: TokenApi.startTask})
const stopTask = () => apiClient.post({ url: TokenApi.stopTask})
const statusTask = () => apiClient.get({ url: TokenApi.statusTask}).then(res => {
  return res
})


export default {
  getTokenList,
  searchTokenList,
  addToken,
  updateToken,
  deleteToken,
  refreshToken,
  startTask,
  stopTask,
  statusTask
};
