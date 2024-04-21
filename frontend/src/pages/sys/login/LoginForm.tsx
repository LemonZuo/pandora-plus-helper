import { Button, Form, Input, Tabs } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { SignInReq } from '@/api/services/userService';
import { useSignIn } from '@/store/userStore';
import { useCaptchaSiteKey } from "@/store/settingStore";
import HCaptcha from "@hcaptcha/react-hcaptcha";

function LoginForm() {
  const { t } = useTranslation();
  const [oauthForm] = Form.useForm();
  const [managerForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [captchaToken, setCaptchaToken] = useState<string | undefined>(undefined);

  const captchaSiteKey = useCaptchaSiteKey();
  const signIn = useSignIn();

  const handleOAuthLogin = async ({ password }: SignInReq) => {
    setLoading(true);
    try {
      await signIn({ type: 1, password, token: captchaToken });
    } finally {
      setLoading(false);
    }
  };

  const handleManagerLogin = async ({ password }: SignInReq) => {
    setLoading(true);
    try {
      await signIn({ type: 2, password, token: captchaToken });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Tabs defaultActiveKey="1" centered>
      <Tabs.TabPane tab={t('sys.login.oauthLogin')} key="1">
        <>
          <Form
            form={oauthForm}
            name="oauth_login"
            size="large"
            onFinish={handleOAuthLogin}
          >
            <Form.Item
              name="password"
              rules={[{ required: true, message: t('sys.login.passwordPlaceholder') }]}
            >
              <Input.Password placeholder={t('sys.login.password')} autoFocus/>
            </Form.Item>
            {captchaSiteKey &&
              <div className="flex flex-row justify-center">
                <Form.Item name="token">
                  <HCaptcha sitekey={captchaSiteKey} onVerify={setCaptchaToken} />
                </Form.Item>
              </div>
            }
            <Form.Item>
              <Button type="primary" htmlType="submit" className="w-full" loading={loading}>
                {t('sys.login.loginButton')}
              </Button>
            </Form.Item>
          </Form>
        </>
      </Tabs.TabPane>
      <Tabs.TabPane tab={t('sys.login.managerLogin')} key="2">
        <>
          <Form
            form={managerForm}
            name="manager_login"
            size="large"
            onFinish={handleManagerLogin}
          >
            <Form.Item
              name="password"
              rules={[{ required: true, message: t('sys.login.passwordPlaceholder') }]}
            >
              <Input.Password placeholder={t('sys.login.password')} autoFocus/>
            </Form.Item>
            {captchaSiteKey &&
              <div className="flex flex-row justify-center">
                <Form.Item name="token">
                  <HCaptcha sitekey={captchaSiteKey} onVerify={setCaptchaToken} />
                </Form.Item>
              </div>
            }
            <Form.Item>
              <Button type="primary" htmlType="submit" className="w-full" loading={loading}>
                {t('sys.login.loginButton')}
              </Button>
            </Form.Item>
          </Form>
        </>
      </Tabs.TabPane>
    </Tabs>
  );
}

export default LoginForm;
