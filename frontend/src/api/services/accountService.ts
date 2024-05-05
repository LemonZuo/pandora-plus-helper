import apiClient from '../apiClient';

import {Account} from '#/entity';

export enum AccountApi {
  list = '/account/list',
  add = '/account/add',
  search = '/account/search',
  delete = '/account/delete',
  update = '/account/update',
  statistic = '/account/statistic',
  chatAuth = '/auth',
}

const getAccountList = () => apiClient.get<Account[]>({ url: AccountApi.list });
const addAccount = (data: Account) => apiClient.post({ url: AccountApi.add, data });
const updateAccount = (data: Account) => apiClient.post({ url: AccountApi.update, data });
const deleteAccount = (data: Account) => apiClient.post({ url: AccountApi.delete, data });
const searchAccount = (tokenId?: number) => apiClient.post({ url: AccountApi.search, data: {
  tokenId,
}});

const chatAuthAccount = (data: Account) => apiClient.post({
  url: AccountApi.chatAuth,
  data: {
    type: 1,
    password: data.password,
  }
});

type AccountStatistic = {
  series: ApexAxisChartSeries;
  categories: string[]
}

const getAccountStatistic = (tokenId: number) => apiClient.post<AccountStatistic>({ url: AccountApi.statistic, data: { tokenId } });

export default {
  getAccountList,
  addAccount,
  updateAccount,
  searchAccount,
  deleteAccount,
  getAccountStatistic,
  chatAuthAccount
};
