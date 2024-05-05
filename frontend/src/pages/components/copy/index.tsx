import React from 'react';
import { Input, Button, message } from 'antd';
import { CopyOutlined } from '@ant-design/icons';

// 定义组件的 props 类型
interface CopyToClipboardInputProps {
  text: string;  // 指定 text 为 string 类型
}

const CopyToClipboardInput: React.FC<CopyToClipboardInputProps> = ({ text }) => {
  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      message.success('复制成功');
    } catch (err) {
      message.error('复制失败');
    }
  };

  return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
        <Input value={text} readOnly style={{ flex: 1 }} />
        <Button icon={<CopyOutlined />} onClick={() => handleCopy(text)} />
      </div>
  );
};

export default CopyToClipboardInput;
