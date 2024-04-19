import apiClient from '../apiClient';

import {Account} from '#/entity';

export enum AccountApi {
  list = '/account/list',
  add = '/account/add',
  search = '/account/search',
  delete = '/account/delete',
  update = '/account/update',
  statistic = '/account/statistic'
}

const getAccountList = () => apiClient.get<Account[]>({ url: AccountApi.list });
const addAccount = (data: Account) => apiClient.post({ url: AccountApi.add, data });
const updateAccount = (data: Account) => apiClient.post({ url: AccountApi.update, data });
const deleteAccount = (data: Account) => apiClient.post({ url: AccountApi.delete, data });
const searchAccount = (tokenId?: number) => apiClient.post({ url: AccountApi.search, data: {
  tokenId,
}});

type AccountStatistic = {
  series: ApexAxisChartSeries;
  categories: string[]
}

const getAccountStatistic = (accountId: number) => apiClient.post<AccountStatistic>({ url: AccountApi.statistic, data: { accountId } });

export default {
  getAccountList,
  addAccount,
  updateAccount,
  searchAccount,
  deleteAccount,
  getAccountStatistic
};
