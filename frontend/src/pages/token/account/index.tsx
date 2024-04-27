// import { useQuery } from '@tanstack/react-query';
import {
  Button,
  Card,
  Col,
  Form,
  Input,
  Popconfirm,
  Row,
  Space, Tooltip,
  // Typography,
} from 'antd';
import Table, { ColumnsType } from 'antd/es/table';
import {useEffect, useState} from 'react';

import {Account} from '#/entity';
import {
  CheckCircleOutlined, CloseCircleOutlined,
  DeleteOutlined, EditOutlined, ExclamationCircleOutlined, MinusCircleOutlined,
} from "@ant-design/icons";
import {useQuery} from "@tanstack/react-query";
import {useSearchParams} from "@/router/hooks";
import accountService from "@/api/services/accountService.ts";
import {useDeleteAccountMutation, useUpdateAccountMutation} from "@/store/accountStore.ts";
import {AccountModal, AccountModalProps} from "src/pages/token/token";
import {useTranslation} from "react-i18next";
type SearchFormFieldType = {
  tokenId?: number;
};

export default function SharePage() {

  const deleteShareMutation = useDeleteAccountMutation()
  const updateShareMutation = useUpdateAccountMutation()

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
      gpt35Limit: -1,
      gpt4Limit: -1,
      showConversations: 'False',
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


  useEffect(() => {
    searchForm.setFieldValue('tokenId', params.get('tokenId'))
  }, [params]);

  const columns: ColumnsType<Account> = [
    { title: t('token.tokenId'), dataIndex: 'tokenId', align: 'center', width: 80 },
    { title: 'Account', dataIndex: 'account', align: 'center', width: 120 },
    { title: t('token.password'), dataIndex: 'password', align: 'center', width: 120 },
    { title: 'ShareToken', dataIndex: 'shareToken', align: 'center',
      render: (text) => (
        <Input value={text} readOnly/>
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
        if (text === 'True') {
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
    { title: t('token.expireAt'), dataIndex: 'expireAt', align: 'center', width: 200 },
    { title: t('token.createTime'), dataIndex: 'createTime', align: 'center', width: 200 },
    { title: t('token.updateTime'), dataIndex: 'updateTime', align: 'center', width: 200 },
    {
      title: t('token.action'),
      key: 'operation',
      align: 'center',
      render: (_,record) => (
        <Button.Group>
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
                <Button type="primary" className="ml-4" onClick={() => {
                  searchForm.validateFields().then((values) => {
                    console.log(values)
                    searchForm.submit()
                  })
                }}>
                  {t('token.search')}
                </Button>
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
