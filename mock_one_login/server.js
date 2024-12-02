/* eslint-disable no-console */

const assert = require('assert');
const camelCase = require('camelcase');

const Provider = require('oidc-provider');
const configLoader = require("./configLoader");


const host = process.env.HOST || 'localhost';
const port = process.env.PORT || 3000;

const config = ['CLIENT_ID', 'CLIENT_SECRET', 'CLIENT_REDIRECT_URI', 'CLIENT_LOGOUT_REDIRECT_URI'].reduce((acc, v) => {
    assert(process.env[v], `${v} config missing`);
    acc[camelCase(v)] = process.env[v];
    return acc;
}, {});

const people_config = configLoader.getConfig('./mock-people.yaml');


const oidcConfig = {
    features: {
        devInteractions: true,
        discovery: true,
        registration: false,
        revocation: true,
        sessionManagement: false
    },
    format: {
        default: 'jwt',
            AccessToken: 'jwt',
            RefreshToken: 'jwt'
    },
    claims: {
        acr: null,
        sid: null,
        auth_time: null,
        iss: null,
        openid: ['sub', 'name', 'email']
    },
    findById: function (ctx, id) {
        console.log("findById called with id ", id)
        if (people_config.people[id]) {
            let person = people_config.people[id];
            return {
                accountId: id,
                async claims(use, scope) {
                    return {
                        sub: id,
                        name: person.name,
                        email: person.email,
                    };
                },
            };
        }
    }
};

const oidc = new Provider(`http://${host}:${port}`, oidcConfig);

const clients = [
    {
        client_id: config.clientId,
        client_secret: config.clientSecret,
        redirect_uris: [config.clientRedirectUri],
        post_logout_redirect_uris: [config.clientLogoutRedirectUri],
        token_endpoint_auth_method: 'private_key_jwt',
        jwks: {
            keys: [
                {
                    alg: 'RS256',
                    d: 'VEZOsY07JTFzGTqv6cC2Y32vsfChind2I_TTuvV225_-0zrSej3XLRg8iE_u0-3GSgiGi4WImmTwmEgLo4Qp3uEcxCYbt4NMJC7fwT2i3dfRZjtZ4yJwFl0SIj8TgfQ8ptwZbFZUlcHGXZIr4nL8GXyQT0CK8wy4COfmymHrrUoyfZA154ql_OsoiupSUCRcKVvZj2JHL2KILsq_sh_l7g2dqAN8D7jYfJ58MkqlknBMa2-zi5I0-1JUOwztVNml_zGrp27UbEU60RqV3GHjoqwI6m01U7K0a8Q_SQAKYGqgepbAYOA-P4_TLl5KC4-WWBZu_rVfwgSENwWNEhw8oQ',
                    dp: 'E1Y-SN4bQqX7kP-bNgZ_gEv-pixJ5F_EGocHKfS56jtzRqQdTurrk4jIVpI-ZITA88lWAHxjD-OaoJUh9Jupd_lwD5Si80PyVxOMI2xaGQiF0lbKJfD38Sh8frRpgelZVaK_gm834B6SLfxKdNsP04DsJqGKktODF_fZeaGFPH0',
                    dq: 'F90JPxevQYOlAgEH0TUt1-3_hyxY6cfPRU2HQBaahyWrtCWpaOzenKZnvGFZdg-BuLVKjCchq3G_70OLE-XDP_ol0UTJmDTT-WyuJQdEMpt_WFF9yJGoeIu8yohfeLatU-67ukjghJ0s9CBzNE_LrGEV6Cup3FXywpSYZAV3iqc',
                    e: 'AQAB',
                    kid: 'keystore-CHANGE-ME',
                    kty: 'RSA',
                    n: 'xwQ72P9z9OYshiQ-ntDYaPnnfwG6u9JAdLMZ5o0dmjlcyrvwQRdoFIKPnO65Q8mh6F_LDSxjxa2Yzo_wdjhbPZLjfUJXgCzm54cClXzT5twzo7lzoAfaJlkTsoZc2HFWqmcri0BuzmTFLZx2Q7wYBm0pXHmQKF0V-C1O6NWfd4mfBhbM-I1tHYSpAMgarSm22WDMDx-WWI7TEzy2QhaBVaENW9BKaKkJklocAZCxk18WhR0fckIGiWiSM5FcU1PY2jfGsTmX505Ub7P5Dz75Ygqrutd5tFrcqyPAtPTFDk8X1InxkkUwpP3nFU5o50DGhwQolGYKPGtQ-ZtmbOfcWQ',
                    p: '5wC6nY6Ev5FqcLPCqn9fC6R9KUuBej6NaAVOKW7GXiOJAq2WrileGKfMc9kIny20zW3uWkRLm-O-3Yzze1zFpxmqvsvCxZ5ERVZ6leiNXSu3tez71ZZwp0O9gys4knjrI-9w46l_vFuRtjL6XEeFfHEZFaNJpz-lcnb3w0okrbM',
                    q: '3I1qeEDslZFB8iNfpKAdWtz_Wzm6-jayT_V6aIvhvMj5mnU-Xpj75zLPQSGa9wunMlOoZW9w1wDO1FVuDhwzeOJaTm-Ds0MezeC4U6nVGyyDHb4CUA3ml2tzt4yLrqGYMT7XbADSvuWYADHw79OFjEi4T3s3tJymhaBvy1ulv8M',
                    qi: 'wSbXte9PcPtr788e713KHQ4waE26CzoXx-JNOgN0iqJMN6C4_XJEX-cSvCZDf4rh7xpXN6SGLVd5ibIyDJi7bbi5EQ5AXjazPbLBjRthcGXsIuZ3AtQyR0CEWNSdM7EyM5TRdyZQ9kftfz9nI03guW3iKKASETqX2vh0Z8XRjyU',
                    use: 'sig',
                },
            ],
        }
    }
];

let server;
(async () => {
    await oidc.initialize({clients});
    console.log("starting server with config ", config)
    server = oidc.listen(port, () => {
        console.log(
            `mock-oidc-user-server listening on port ${port}, check http://${host}:${port}/.well-known/openid-configuration`
        );
    });
})().catch(err => {
    if (server && server.listening) server.close();
    console.error(err);
    process.exitCode = 1;
});
