// Code generated by wunderctl. DO NOT EDIT.

import type { OperationArgsWithInput, InternalClient as BaseClient } from "@wundergraph/sdk/server";
import type { OperationErrors } from "./ts-operation-errors";
import {
	ScriptsResponse,
	ScriptsResponseData,
	UsersGetResponse,
	UsersGetResponseData,
	UsersSubscribeResponse,
	UsersSubscribeResponseData,
	UsersUpdateResponse,
	UsersUpdateInput,
	UsersUpdateInputInternal,
	UsersUpdateResponseData,
} from "./models";

export interface Queries {
	Scripts: () => Promise<{ data?: ScriptsResponse["data"]; errors?: Required<ScriptsResponse>["errors"] }>;
	UsersGet: () => Promise<{ data?: UsersGetResponseData; errors?: OperationErrors["users/get"][] }>;
}

export interface Mutations {
	UsersUpdate: (
		options: OperationArgsWithInput<UsersUpdateInputInternal>
	) => Promise<{ data?: UsersUpdateResponseData; errors?: OperationErrors["users/update"][] }>;
}

export interface InternalClient extends BaseClient<Queries, Mutations> {}