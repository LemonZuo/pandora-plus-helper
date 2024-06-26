import { BasicStatus, PermissionType } from './enum';

export interface UserToken {
  accessToken?: string
}

export interface UserInfo {
  id: string;
  email: string;
  username: string;
  password?: string;
  avatar?: string;
  role?: Role;
  status?: BasicStatus;
  permissions?: Permission[];
}

export interface Organization {
  id: string;
  name: string;
  status: 'enable' | 'disable';
  desc?: string;
  order?: number;
  children?: Organization[];
}

export interface Permission {
  id: string;
  parentId: string;
  name: string;
  label: string;
  type: PermissionType;
  route: string;
  status?: BasicStatus;
  order?: number;
  icon?: string;
  component?: string;
  hide?: boolean;
  frameSrc?: string;
  newFeature?: boolean;
  children?: Permission[];
}

export interface Role {
  id: string;
  name: string;
  label: string;
  status: BasicStatus;
  order?: number;
  desc?: string;
  permission?: Permission[];
}

export interface Token {
  id: number;
  tokenName: string;
  plusSubscription?: number;
  refreshToken: string;
  accessToken?: string;
  expireAt?: string;
  createTime?: string;
  updateTime?: string;
}

export interface Account {
  id?: number;
  account: string;
  password: string;
  status: 1 | 0;
  expirationTime?: string;
  tokenId: number;
  gpt35Limit: number;
  gpt4Limit: number;
  showConversations: 0 | 1;
  temporaryChat: 0 | 1;
  shareToken?: string;
  expireAt?: string;
  createTime?: string;
  updateTime?: string;
}
