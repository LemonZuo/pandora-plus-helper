import {
  Badge,
  Button,
  Card,
  Col,
  Form,
  Input,
  Modal,
  Popconfirm,
  Row,
  Select,
  Space,
  Spin, Tooltip,
  Typography,
} from 'antd';
import Table, {ColumnsType} from 'antd/es/table';
import {useEffect, useState} from 'react';

// import ProTag from '@/theme/antd/components/tag';
import {Account, Token} from '#/entity';
import {
  CaretRightFilled, CheckCircleOutlined, DeleteOutlined,
  EditOutlined, FundOutlined, MinusCircleOutlined,
  PauseCircleFilled,
  PlusOutlined, QuestionCircleOutlined,
  ReloadOutlined,
  ShareAltOutlined
} from "@ant-design/icons";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import tokenService, {TokenAddReq,} from "@/api/services/tokenService.ts";
import {useNavigate} from "react-router-dom";
import {useAddAccountMutation} from "@/store/accountStore.ts";
import {
  useAddTokenMutation,
  useDeleteTokenMutation,
  useRefreshTokenMutation,
  useUpdateTokenMutation
} from "@/store/tokenStore.ts";
import Chart from "@/components/chart/chart.tsx";
import useChart from "@/components/chart/useChart.ts";
import accountService from "@/api/services/accountService.ts";
import {useTranslation} from "react-i18next";

type SearchFormFieldType = Pick<Token, 'tokenName'>;


const { Option } = Select;
export default function TokenPage() {
  const [searchForm] = Form.useForm();
  const {t} = useTranslation()
  const client = useQueryClient();

  const addTokenMutation = useAddTokenMutation();
  const updateTokenMutation = useUpdateTokenMutation();
  const deleteTokenMutation = useDeleteTokenMutation();
  const refreshTokenMutation = useRefreshTokenMutation();
  const addAccountMutation = useAddAccountMutation();

  const navigate = useNavigate();

  const [deleteTokenId, setDeleteTokenId] = useState<number | undefined>(-1);
  const [refreshTokenId, setRefreshTokenId] = useState<number | undefined>(-1);

  const searchEmail = Form.useWatch('tokenName', searchForm);


  const [TokenModalPros, setTokenModalProps] = useState<TokenModalProps>({
    formValue: {
      tokenName: '',
      refreshToken: '',
    },
    title: 'New',
    show: false,
    onOk: (values: TokenAddReq, callback) => {
      if (values.id) {
        updateTokenMutation.mutate(values, {
          onSuccess: () => {
            setTokenModalProps((prev) => ({...prev, show: false}))
          },
          onSettled: () => callback(false)
        });
      } else {
        addTokenMutation.mutate(values, {
          onSuccess: () => {
            setTokenModalProps((prev) => ({...prev, show: false}))
          },
          onSettled: () => callback(false)
        });
      }
    },
    onCancel: () => {
      setTokenModalProps((prev) => ({...prev, show: false}));
    },
  });

  const [shareModalProps, setAccountModalProps] = useState<AccountModalProps>({
    formValue: {
      tokenId: -1,
      account: '',
      password: '',
      gpt35Limit: -1,
      gpt4Limit: -1,
      showConversations: 'False',
    },
    title: 'New',
    show: false,
    isEdit: false,
    onOk: (values: Account, callback) => {
      callback(true);
      addAccountMutation.mutate(values, {
        onSuccess: () => {
          setAccountModalProps((prev) => ({...prev, show: false}))
        },
        onSettled: () => callback(false)
      });
    },
    onCancel: () => {
      setAccountModalProps((prev) => ({...prev, show: false}));
    },
  });

  const [shareInfoModalProps, setAccountInfoModalProps] = useState<AccountInfoModalProps>({
    tokenId: -1,
    show: false,
    onOk: () => {
      setAccountInfoModalProps((prev) => ({...prev, show: false}));
    },
  });

  const columns: ColumnsType<Token> = [
    {
      title: t('token.id'), dataIndex: 'id', ellipsis: true, align: 'center',
      render: (text) => (
        <Typography.Text style={{maxWidth: 200}} ellipsis={true}>
          {text}
        </Typography.Text>
      )
    },
    {
      title: t('token.tokenName'), dataIndex: 'tokenName', align: 'center', ellipsis: true,
      render: (text) => (
        <Typography.Text style={{maxWidth: 200}} ellipsis={true}>
          {text}
        </Typography.Text>
      )
    },
    {
      title: t('token.plusSubscription'),
      dataIndex: 'plusSubscription',
      align: 'center',
      render: (subscription) => {
        if (subscription === -1) {
          return <Tooltip title={t('token.subscriptionUnknown')}><QuestionCircleOutlined style={{ color: 'gray' }} /></Tooltip>;
        } else if (subscription === 0) {
          return <Tooltip title={t('token.unsubscribed')}><MinusCircleOutlined style={{ color: 'red' }} /></Tooltip>;
        } else if (subscription === 1) {
          return <Tooltip title={t('token.subscribed')}><CheckCircleOutlined style={{ color: 'green' }} /></Tooltip>;
        }
      },
    },
    { title: t('token.refreshToken'), dataIndex: 'refreshToken', align: 'center',
      render: (text) => (
        <Input value={text} readOnly/>
      ),
    },
    { title: t('token.accessToken'),
      dataIndex: 'accessToken',
      align: 'center',
      render: (text) => (
        <Input value={text} readOnly/>
      ),
    },
    {
      title: t("token.expireAt"),
      dataIndex: 'expireAt',
      align: 'center',
      width: 200,
    },
    {
      title: t("token.createTime"),
      dataIndex: 'createTime',
      align: 'center',
      width: 200,
    },
    {
      title: t("token.updateTime"),
      dataIndex: 'updateTime',
      align: 'center',
      width: 200,
    },
    {
      title: t('token.share'),
      key: 'share',
      align: 'center',
      render: (_, record) => (
        <Button.Group>
          <Badge style={{zIndex: 9}}>
            <Button icon={<ShareAltOutlined />} onClick={() => navigate({
              pathname: '/token/account',
              search: `?tokenId=${record.id}`,
            })}>
              {t('token.shareList')}
            </Button>
          </Badge>
          <Button icon={<PlusOutlined />} onClick={() => onAccountAdd(record)}/>
          <Button icon={<FundOutlined />} onClick={() => onAccountInfo(record)}/>
        </Button.Group>
      ),
    },
    {
      title: t('token.action'),
      key: 'operation',
      align: 'center',
      render: (_, record) => (
        <Button.Group>
          <Popconfirm title={t('common.refreshConfirm')} okText="Yes" cancelText="No" placement="left" onConfirm={() => {
            setRefreshTokenId(record.id);
            refreshTokenMutation.mutate(record.id, {
              onSettled: () => setRefreshTokenId(undefined),
            })
          }}>
            <Button key={record.id} icon={<ReloadOutlined/>} type={"primary"} loading={refreshTokenId === record.id}>
              {t('common.refresh')}
            </Button>
          </Popconfirm>
          <Button onClick={() => onEdit(record)} icon={<EditOutlined/>} type={"primary"}/>
          <Popconfirm title={t('common.deleteConfirm')} okText="Yes" cancelText="No" placement="left" onConfirm={() => {
            setDeleteTokenId(record.id);
            deleteTokenMutation.mutate(record.id, {
              onSuccess: () => setDeleteTokenId(undefined)
            })
          }}>
            <Button icon={<DeleteOutlined/>} type={"primary"} loading={deleteTokenId === record.id} danger/>
          </Popconfirm>
        </Button.Group>
      ),
    },
  ];

  const {data} = useQuery({
    queryKey: ['accounts', searchEmail],
    queryFn: () => tokenService.searchTokenList(searchEmail)
  })

  const {data: taskStatus} = useQuery({
    queryKey: ['taskStatus'],
    queryFn: () => tokenService.statusTask(),
  })

  const startTask = useMutation(tokenService.startTask, {
      onSuccess: () => {
        client.invalidateQueries(['taskStatus']);
        console.log('startTask success');
      }
    }
  )

  const stopTask = useMutation(tokenService.stopTask, {
      onSuccess: () => {
        client.invalidateQueries(['taskStatus']);
        console.log('stopTask success');
      }
    }
  )

  const onSearchFormReset = () => {
    searchForm.resetFields();
  };

  const onCreate = () => {
    setTokenModalProps((prev) => ({
      ...prev,
      show: true,
      title: t('token.createNew'),
      formValue: {
        id: undefined,
        tokenName: '',
        refreshToken: '',
      },
    }));
  };

  const onAccountAdd = (record: Token) => {
    setAccountModalProps((prev) => ({
      ...prev,
      show: true,
      title: t('token.share'),
      formValue: {
        tokenId: record.id,
        account: '',
        password: '',
        gpt35Limit: -1,
        gpt4Limit: -1,
        showConversations: 'False',
      },
    }));
  }

  const onAccountInfo = (record: Token) => {
    setAccountInfoModalProps((prev) => ({
      ...prev,
      show: true,
      isEdit: false,
      tokenId: record.id,
    }));
  }

  const onEdit = (record: Token) => {
    console.log(record);

    setTokenModalProps((prev) => ({
      ...prev,
      show: true,
      title: t('token.edit'),
      formValue: {
        ...prev.formValue,
        id: record.id,
        tokenName: record.tokenName,
        refreshToken: record.refreshToken,
      }
    }));
  };

  return (
    <Space direction="vertical" size="large" className="w-full">
      <Card>
        <Form form={searchForm}>
          <Row gutter={[16, 16]}>
            <Col span={6} lg={6}>
              <Form.Item<SearchFormFieldType> label={t('token.tokenName')} name="tokenName" className="!mb-0">
                <Input/>
              </Form.Item>
            </Col>
            <Col span={18} lg={18}>
              <div className="flex justify-end">
                <Button onClick={onSearchFormReset}>{t('token.reset')}</Button>
                <Button type="primary" className="ml-4">
                  {t('token.search')}
                </Button>
              </div>
            </Col>
          </Row>
        </Form>
      </Card>

      <Card
        title={t("token.accountList")}
        extra={
          <Space>
            {taskStatus?.status ? <Button icon={<PauseCircleFilled/>} onClick={() => stopTask.mutate()}>{t("token.stop")}</Button> : <Button icon={<CaretRightFilled/>} onClick={() => startTask.mutate()}>{t("token.start")}</Button>}
            <Button type="primary" onClick={onCreate}>
              {t("token.createNew")}
            </Button>
          </Space>

        }
      >
        <Table
          rowKey="id"
          size="small"
          scroll={{x: 'max-content'}}
          pagination={{pageSize: 10}}
          columns={columns}
          dataSource={data}
        />
      </Card>
      <TokenModal {...TokenModalPros} />
      <AccountModal {...shareModalProps} />
      <AccountInfoModal {...shareInfoModalProps}/>
    </Space>
  );
}

export type AccountModalProps = {
  formValue: Account;
  title: string;
  show: boolean;
  isEdit: boolean;
  onOk: (values: Account, callback: any) => void;
  onCancel: VoidFunction;
}

export const AccountModal = ({title, show, isEdit, formValue, onOk, onCancel}: AccountModalProps) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const {t} = useTranslation()

  useEffect(() => {
    form.setFieldsValue({...formValue});
  }, [formValue, form]);

  const onModalOk = () => {
    form.validateFields().then((values) => {
      onOk(values, setLoading);
    });
  }

  return (
    <Modal title={title} open={show} onOk={onModalOk} onCancel={() => {
      form.resetFields();
      onCancel();
    }} okButtonProps={{
      loading: loading,
    }} destroyOnClose={false}>
      <Form
        initialValues={formValue}
        form={form}
        layout="vertical"
        preserve={false}
      >
        <Form.Item<Account> name="id" hidden>
          <Input/>
        </Form.Item>
        <Form.Item<Account> name="tokenId" hidden>
          <Input/>
        </Form.Item>
        <Form.Item<Account> label="Account" name="account" required>
          <Input readOnly={isEdit} disabled={isEdit}/>
        </Form.Item>
        <Form.Item<Account> label={t('token.password')} name="password" required>
          <Input.Password/>
        </Form.Item>
        <Form.Item<Account> label={t('token.gpt35Limit')} name="gpt35Limit" required>
          <Input/>
        </Form.Item>
        <Form.Item<Account> label={t('token.gpt4Limit')} name="gpt4Limit" required>
          <Input/>
        </Form.Item>
        <Form.Item<Account> label={t('token.showConversations')} name="showConversations" initialValue="False" required>
          <Select allowClear>
            <Option value="True">{t('common.yes')}</Option>
            <Option value="False">{t('common.no')}</Option>
          </Select>
        </Form.Item>
      </Form>
    </Modal>
  );
}

type TokenModalProps = {
  formValue: TokenAddReq;
  title: string;
  show: boolean;
  onOk: (values: TokenAddReq, setLoading: any) => void;
  onCancel: VoidFunction;
};

function TokenModal({title, show, formValue, onOk, onCancel}: TokenModalProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const {t} = useTranslation()

  const onModalOk = () => {
    form.validateFields().then((values) => {
      setLoading(true)
      onOk(values, setLoading);
    });
  }
  return (
    <Modal title={title} open={show} onOk={onModalOk} onCancel={() => {
      form.resetFields();
      onCancel();
    }} okButtonProps={{
      loading: loading,
    }} destroyOnClose={false}>
      <Form
        initialValues={formValue}
        form={form}
        layout="vertical"
        preserve={false}
      >
        <Form.Item<TokenAddReq> name="id" hidden>
          <Input/>
        </Form.Item>
        <Form.Item<TokenAddReq> label={t("token.tokenName")} name="tokenName" required>
          <Input/>
        </Form.Item>
        <Form.Item<TokenAddReq> label={t("token.refreshToken")} name="refreshToken" required>
          <Input/>
        </Form.Item>

      </Form>
    </Modal>
  );
}

type AccountInfoModalProps = {
  tokenId: number
  onOk: VoidFunction
  show: boolean;
}

const AccountInfoModal = ({tokenId, onOk, show}: AccountInfoModalProps) => {

  const {data: statistic, isLoading} = useQuery({
    queryKey: ['shareInfo', tokenId],
    queryFn: () => accountService.getAccountStatistic(tokenId),
    enabled: show,
  })

  const {t} = useTranslation()

  let chartOptions = useChart({
    legend: {
      horizontalAlign: 'center',
    },
    stroke: {
      show: true,
    },
    dataLabels: {
      enabled: true,
      dropShadow: {
        enabled: false,
      },
    },
    xaxis: {
      categories: statistic?.categories || [],
    },
    tooltip: {
      fillSeriesColor: false,
    },
    plotOptions: {
      pie: {
        donut: {
          labels: {
            show: false,
          },
        },
      },
    },
  });

  return (
    <Modal title={t('token.statistic')} open={show} onOk={onOk} closable={false} onCancel={onOk}>
      <Spin spinning={isLoading} tip={t("token.queryingInfo")}>
        <Chart type="bar" series={statistic?.series || []} options={chartOptions} height={320}/>
      </Spin>
    </Modal>
  )
}
