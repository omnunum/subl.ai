// wundergraph.config.ts
var import_sdk2 = require("@wundergraph/sdk");

// wundergraph.server.ts
var import_graphql = require("graphql");
var import_server = require("@wundergraph/sdk/server");
var wundergraph_server_default = (0, import_server.configureWunderGraphServer)(() => ({
  hooks: {
    queries: {},
    mutations: {}
  },
  graphqlServers: [
    {
      serverName: "gql",
      apiNamespace: "gql",
      schema: new import_graphql.GraphQLSchema({
        query: new import_graphql.GraphQLObjectType({
          name: "RootQueryType",
          fields: {
            hello: {
              type: import_graphql.GraphQLString,
              resolve() {
                return "world";
              }
            }
          }
        })
      })
    }
  ]
}));

// wundergraph.operations.ts
var import_sdk = require("@wundergraph/sdk");
var wundergraph_operations_default = (0, import_sdk.configureWunderGraphOperations)({
  operations: {
    defaultConfig: {
      authentication: {
        required: false
      }
    },
    queries: (config) => ({
      ...config,
      caching: {
        enable: false,
        staleWhileRevalidate: 60,
        maxAge: 60,
        public: true
      },
      liveQuery: {
        enable: true,
        pollingIntervalSeconds: 1
      }
    }),
    mutations: (config) => ({
      ...config
    }),
    subscriptions: (config) => ({
      ...config
    }),
    custom: {}
  }
});

// wundergraph.config.ts
var db = import_sdk2.introspect.postgresql({
  apiNamespace: "db",
  databaseURL: new import_sdk2.EnvironmentVariable("DATABASE_URL")
});
(0, import_sdk2.configureWunderGraphApplication)({
  apis: [db],
  server: wundergraph_server_default,
  operations: wundergraph_operations_default,
  generate: {
    codeGenerators: []
  },
  cors: {
    ...import_sdk2.cors.allowAll,
    allowedOrigins: ["http://localhost:3000"]
  },
  security: {
    enableGraphQLEndpoint: true
  }
});
//# sourceMappingURL=config.cjs.map
