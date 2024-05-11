// import { useQuery } from '@tanstack/react-query';
import {
  Button,
  Card,
  Col,
  Form,
  Input, message,
  Popconfirm,
  Row,
  Space, Tooltip,
  // Typography,
} from 'antd';
import Table, { ColumnsType } from 'antd/es/table';
import {useEffect, useState} from 'react';

import {Account} from '#/entity';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  DeleteOutlined,
  EditOutlined,
  ExclamationCircleOutlined,
  MinusCircleOutlined,
  OpenAIFilled,
  StopOutlined,
} from '@ant-design/icons';
import {useQuery} from "@tanstack/react-query";
import {useSearchParams} from "@/router/hooks";
import accountService from "@/api/services/accountService.ts";
import {
  useDeleteAccountMutation, useDisableAccountMutation,
  useEnableAccountMutation,
  useUpdateAccountMutation,
} from '@/store/accountStore.ts';
import {AccountModal, AccountModalProps} from "src/pages/token/token";
import {useTranslation} from "react-i18next";
import CopyToClipboardInput from '@/pages/components/copy';
type SearchFormFieldType = {
  tokenId?: number;
};

export default function SharePage() {

  const deleteShareMutation = useDeleteAccountMutation()
  const updateShareMutation = useUpdateAccountMutation()
  const disableShareMutation = useDisableAccountMutation()
  const enableShareMutation = useEnableAccountMutation()

  const {t} = useTranslation()

  const params = useSearchParams();
  const [searchForm] = Form.useForm();
  const tokenId = Form.useWatch('tokenId', searchForm);
  const [deleteRowKey, setDeleteRowKey] = useState<string | undefined>(undefined);
  const [shareModalProps, setShareModalProps] = useState<AccountModalProps>({
    formValue: {
      tokenId: -1,
      account: '',
      password: '',
      status: 1,
      expirationTime: '',
      gpt35Limit: -1,
      gpt4Limit: -1,
      showConversations: 0,
      temporaryChat: 0,
    },
    title: t('token.edit'),
    show: false,
    isEdit: false,
    onOk: (values: Account) => {
      console.log(values)
      setShareModalProps((prev) => ({...prev, show: false}));
    },
    onCancel: () => {
      setShareModalProps((prev) => ({...prev, show: false}));
    },
  });
  const [chatAccountId, setChatAccountId] = useState<number | undefined>(-1);


  useEffect(() => {
    searchForm.setFieldValue('tokenId', params.get('tokenId'))
  }, [params]);

  function handleQuickLogin(record: Account) {
    setChatAccountId(record.id)
    accountService.chatAuthAccount(record)
      .then((res) => {
        const {loginUrl} = res;
        if (loginUrl) {
          window.open(loginUrl)
        } else {
          message.error('Failed to get login url').then(r => console.log(r))
        }
      })
      .catch((err) => {
        console.log(err)
        message.error('Failed to get login url').then(r => console.log(r))
      })
      .finally(() => {
        setChatAccountId(undefined)
      })
  }

  const columns: ColumnsType<Account> = [
    { title: t('token.tokenId'), dataIndex: 'tokenId', align: 'center', width: 80 },
    { title: 'Account', dataIndex: 'account', align: 'center', width: 120 },
    { title: t('token.password'), dataIndex: 'password', align: 'center', width: 120 },
    {
      title: t('token.accountStatus'),
      dataIndex: 'status',
      align: 'center',
      render: (status) => {
        if (status === 0) {
          return <Tooltip title={t('token.disable')}><CloseCircleOutlined style={{ color: 'red' }} /></Tooltip>;

        } else if (status === 1) {
          return <Tooltip title={t('token.normal')}><CheckCircleOutlined style={{ color: 'green' }} /></Tooltip>;
        }
      },
    },
    {
      title: t('token.expirationTime'),
      dataIndex: 'expirationTime',
      align: 'center',
      width: 200,
    },
    {
      title: 'ShareToken',
      dataIndex: 'shareToken',
      align: 'center',
      render: (text) => (
        <CopyToClipboardInput text={text}/>
      ),
    },
    { title: t('token.gpt35Limit'),
      dataIndex: 'gpt35Limit',
      align: 'center',
      width: 120,
      render: (count) => {
        if (count === 0) {
          // 为0无法使用
          return <Tooltip title={t('token.notAvailable')}><CloseCircleOutlined style={{ color: 'red' }} /></Tooltip>;
        } else if (count < 0) {
          // 负数不限制
          return <Tooltip title={t('token.unlimitedTimes')}><MinusCircleOutlined style={{ color: 'green' }} /></Tooltip>;
        } else {
          // 大于零为限制的具体次数
          return (
            <Tooltip title={`${t('token.limitedTimes')}:${count}`}>
              <ExclamationCircleOutlined style={{ color: 'orange' }} />
            </Tooltip>
          );
        }
      },
    },
    {
      title: t('token.gpt4Limit'),
      dataIndex: 'gpt4Limit',
      align: 'center',
      width: 120,
      render: (count) => {
        if (count === 0) {
          // 为0无法使用
          return <Tooltip title={t('token.notAvailable')}><CloseCircleOutlined style={{ color: 'red' }} /></Tooltip>;
        } else if (count < 0) {
          // 负数不限制
          return <Tooltip title={t('token.unlimitedTimes')}><MinusCircleOutlined style={{ color: 'green' }} /></Tooltip>;
        } else {
          // 大于零为限制的具体次数
          return (
            <Tooltip title={`${t('token.limitedTimes')}:${count}`}>
              <ExclamationCircleOutlined style={{ color: 'orange' }} />
            </Tooltip>
          );
        }
      },
    },
    {
      title: t('token.showConversations'),
      dataIndex: 'showConversations',
      align: 'center',
      width: 120,
      render: (text) => {
        if (text === 1) {
          return (
            <Tooltip title={t('common.yes')}>
              <CheckCircleOutlined style={{ color: 'orange' }} />
            </Tooltip>
          );
        } else {
          return (
            <Tooltip title={t('common.no')}>
              <CloseCircleOutlined style={{ color: 'green' }} />
            </Tooltip>
          );
        }
      },
    },
    {
      title: t('token.temporaryChat'),
      dataIndex: 'temporaryChat',
      align: 'center',
      width: 120,
      render: (text) => {
        if (text === 1) {
          return (
            <Tooltip title={t('common.yes')}>
              <CheckCircleOutlined style={{ color: 'red' }} />
            </Tooltip>
          );
        } else {
          return (
            <Tooltip title={t('common.no')}>
              <CloseCircleOutlined style={{ color: 'green' }} />
            </Tooltip>
          );
        }
      },
    },
    { title: t('token.expireAt'), dataIndex: 'expireAt', align: 'center', width: 200 },
    { title: t('token.createTime'), dataIndex: 'createTime', align: 'center', width: 200 },
    { title: t('token.updateTime'), dataIndex: 'updateTime', align: 'center', width: 200 },
    {
      title: t('token.action'),
      key: 'operation',
      align: 'center',
      render: (_,record) => (
        <Button.Group>
          {
            record.status === 0 ? (<Tooltip title={t('token.enable')}><Button icon={<CheckCircleOutlined />} type="primary" onClick={() => handleEnable(record)}></Button></Tooltip>)
            : record.status === 1 ? (<Tooltip title={t('token.disable')}><Button icon={<StopOutlined />} type="primary" danger onClick={() => handleDisable(record)}></Button></Tooltip>)
            : null
          }
          <Button
            icon={<OpenAIFilled />}
            type={"primary"}
            onClick={() => handleQuickLogin(record)}
            loading={chatAccountId === record.id}
            style={{ backgroundColor: '#007bff', borderColor: '#007bff', color: 'white' }}
            disabled={record.status !== 1}
          >Chat</Button>
          <Button icon={<EditOutlined />} type={"primary"} onClick={() => onEdit(record)}/>
          <Popconfirm title={t('token.deleteConfirm')} okText="Yes" cancelText="No" placement="left" onConfirm={() => handleDelete(record)}>
            <Button icon={<DeleteOutlined />} type={"primary"} loading={deleteRowKey == record.id + record.account}  danger/>
          </Popconfirm>
        </Button.Group>
      ),
    },
  ];

  const onEdit = (record: Account) => {
    setShareModalProps({
      formValue: record,
      title: t('token.edit'),
      show: true,
      isEdit: true,
      onOk: (values: Account, callback) => {
        updateShareMutation.mutate(values, {
          onSuccess: () => {
            setShareModalProps((prev) => ({...prev, show: false}));
          },
          onSettled: () => callback(false)
        })
      },
      onCancel: () => {
        setShareModalProps((prev) => ({...prev, show: false}));
      },
    })
  }

  const handleDelete = (record: Account) => {
    setDeleteRowKey(record.id + record.account)
    deleteShareMutation.mutate(record, {
      onSettled: () => {
        setDeleteRowKey(undefined)
      }
    })
  }

  const handleDisable = (record: Account) => {
    disableShareMutation.mutate(record, {
      onSuccess: () => {
        message.success('Success')
      }
    })
  }

  const handleEnable = (record: Account) => {
    enableShareMutation.mutate(record, {
      onSuccess: () => {
        message.success('Success')
      }
    })
  }

  const { data } = useQuery({
    queryKey: ['shareList', tokenId],
    queryFn: () => {
      return accountService.searchAccount(tokenId)
    }
  })

  const onSearchFormReset = () => {
    searchForm.resetFields();
  };

  return (
    <Space direction="vertical" size="large" className="w-full">
      <Card>
        <Form form={searchForm} >
          <Row gutter={[16, 16]}>
            <Col span={3} lg={3}>
              <Form.Item<SearchFormFieldType> label={t('token.tokenId')} name="tokenId" className="!mb-0">
                <Input />
              </Form.Item>
            </Col>
            <Col span={21} lg={21}>
              <div className="flex justify-end">
                <Button onClick={onSearchFormReset}>{t('token.reset')}</Button>
              </div>
            </Col>
          </Row>
        </Form>
      </Card>

      <Card
        title={t('token.shareList')}
      >
        <Table
          rowKey={record => record.id + record.account}
          size="small"
          scroll={{ x: 'max-content' }}
          pagination={{ pageSize: 10 }}
          columns={columns}
          dataSource={data}
        />
      </Card>
      <AccountModal {...shareModalProps}/>
    </Space>
  );
}
