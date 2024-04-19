import {useMutation, useQueryClient} from "@tanstack/react-query";
import tokenService from "@/api/services/tokenService.ts";
import {message} from "antd";

export const useAddTokenMutation = () => {
  const client = useQueryClient();
  return useMutation(tokenService.addToken, {
    onSuccess: () => {
      /* onSuccess */
      message.success('Add Token Success')
      client.invalidateQueries(['accounts']);
    },
  });
}

export const useUpdateTokenMutation = () => {
  const client = useQueryClient();
  return useMutation(tokenService.updateToken, {
    onSuccess: () => {
      /* onSuccess */
      message.success('Update Token Success')
      client.invalidateQueries(['accounts']);
    },
  });
}

export const useDeleteTokenMutation = () => {
  const client = useQueryClient();
  return useMutation(tokenService.deleteToken, {
    onSuccess: () => {
      /* onSuccess */
      message.success('Delete Token Success')
      client.invalidateQueries(['accounts']);
    }
  });
}

export const useRefreshTokenMutation = () => {
  const client = useQueryClient();
  return useMutation(tokenService.refreshToken, {
    onSuccess: () => {
      /* onSuccess */
      message.success('Refresh Token Success')
      client.invalidateQueries(['accounts']);
    }
  });
}
