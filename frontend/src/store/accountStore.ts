import {useMutation, useQueryClient} from "@tanstack/react-query";
import accountService from "@/api/services/accountService.ts";
import {message} from "antd";


export const useAddAccountMutation = () => {
  const client = useQueryClient();
  return useMutation(accountService.addAccount, {
    onSuccess: () => {
      /* onSuccess */
      client.invalidateQueries(['accounts']);
      message.success('Success')
    },
  });
}

export const useUpdateAccountMutation = () => {
  const client = useQueryClient();
  return useMutation(accountService.updateAccount, {
    onSuccess: () => {
      /* onSuccess */
      client.invalidateQueries(['shareList']);
      message.success('Success')
    },
  });
}

export const useDeleteAccountMutation = () => {
  const client = useQueryClient();
  return useMutation(accountService.deleteAccount, {
    onSuccess: () => {
      /* onSuccess */
      client.invalidateQueries(['shareList']);
      message.success('Success')
    },
  })
}

export default {
  useAddAccountMutation,
  useDeleteAccountMutation,
}

