const Provider = require("oidc-provider");
const assert = require('assert');
const camelCase = require('camelcase');

const SUPPORTED_SCOPES = [
    "address",
    "c",
    "facsimileTelephoneNumber",
    "homeFAX",
    "homeMobile",
    "homePager",
    "homePhone",
    "homePostalAddress",
    "l",
    "localFAX",
    "localMobile",
    "localPager",
    "localPhone",
    "localPostalAddress",
    "mailStop",
    "mobile",
    "pager",
    "postalAddress",
    "postalCode",
    "postOfficeBox",
    "st",
    "street",
    "telephoneNumber",
    "virginiaTechAffiliation",
    "userCertificate",
    "userSMIMECertificate",
    "email_verified",
    "creationDate",
    "birthdate",
    "name",
    "gender",
    "email",
    "personType",
    "uid",
    "uupid",
    "virginiaTechID",
    "department",
    "departmentNumber",
    "title",
    "groupMembershipUugid",
    "pidm",
    "udcIdentifier",
    "mail",
    "bannerName",
    "cn",
    "given_name",
    "initials",
    "middle_name",
    "family_name",
    "instantMessagingID",
    "labeledURI",
    "mailExternalAddress",
    "campus",
    "college",
    "lastEnrollmentTerm",
    "major",
    "nextEnrollmentTerm",
    "studentLevelCode",
    "suppressDisplay",
    "suppressedAttribute",
    "openid",
];

function getProvider(issuerUrl, personRepo) {
    const config = ['CLIENT_ID', 'CLIENT_SECRET', 'CLIENT_REDIRECT_URI', 'CLIENT_LOGOUT_REDIRECT_URI'].reduce((acc, v) => {
        assert(process.env[v], `${v} config missing`);
        acc[camelCase(v)] = process.env[v];
        return acc;
    }, {});

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
                        n: 'xwQ72P9z9OYshiQ-ntDYaPnnfwG6u9JAdLMZ5o0dmjlcyrvwQRdoFIKPnO65Q8mh6F_LDSxjxa2Yzo_wdjhbPZLjfUJXgCzm54cClXzT5twzo7lzoAfaJlkTsoZc2HFWqmcri0BuzmTFLZx2Q7wYBm0pXHmQKF0V-C1O6NWfd4mfBhbM-I1tHYSpAMgarSm22WDMDx-WWI7TEzy2QhaBVaENW9BKaKkJklocAZCxk18WhR0fckIGiWiSM5FcU1PY2jfGsTmX505Ub7P5Dz75Ygqrutd5tFrcqyPAtPTFDk8X1InxkkUwpP3nFU5o50DGhwQolGYKPGtQ-ZtmbOfcWQ',
                        e: 'AQAB',
                        kid: 'keystore-CHANGE-ME',
                        kty: 'RSA',
                        use: 'sig',
                    },
                ],
            }
        }
    ];


    const oidcConfig = {
        findAccount: (_, sub) => {
            if (!personRepo.isValidPerson(sub))
                return undefined;

            return {
                accountId: sub,
                claims: (_, scope) => {
                    return {
                        sub,
                        ...personRepo.getClaims(scope.split(" "), sub),
                    };
                },
            };
        },
        features: {
            // Enables built-in login screens
            devInteractions: {enabled: true},
            registration: {enabled: false},
            revocation: {enabled: true},
            claimsParameter: {enabled: false},
            requestObjects: {enabled: false},
            sessionManagement: {enabled: false},
        },
        formats: {
            default: "jwt",
                AccessToken: 'jwt',
                RefreshToken: 'jwt'
        },
        claims: SUPPORTED_SCOPES.reduce(
            (acc, cur) => ({...acc, [cur]: [cur]}),
            {}
        ),
        clients,
        clientDefaults: {
            grant_types: ["authorization_code"],
            id_token_signed_response_alg: "RS256",
            response_types: ["code"],
            token_endpoint_auth_method: "private_key_jwt",
        },
        conformIdTokenClaims: true,
        issueRefreshToken: () => true,
        subjectTypes: ["pairwise"],
        scopes: SUPPORTED_SCOPES,
        whitelistedJWA: {
            idTokenSigningAlgValues: ["RS256"],
            userinfoSigningAlgValues: ["RS256"],
            requestObjectSigningAlgValues: [],
        },
    };

    const provider = new Provider(issuerUrl, oidcConfig);
    provider.proxy = true;
    return provider;
}

module.exports = getProvider;
