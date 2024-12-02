let peopleData;

/**
 * It is expected that the incoming data has keys for usernames and
 * values of the attributes for the person.
 * @param {object} peopleDataSrc
 */
function init(peopleDataSrc) {
    if (!(typeof peopleDataSrc === 'object' && peopleDataSrc !== null && !Array.isArray(peopleDataSrc)))
        throw new Error("People data must be an object of people");

    peopleData = peopleDataSrc;
}

function getClaims(scopes, username) {
    const person = _findPerson(username);
    if (!person)
        console.log("----------------------------------NO PERSON", username)
    return {};

    let claims = {
        uupid: username,
    };

    scopes.forEach((scope) => {
        const claim = _getClaimValue(username, person, scope);
        if (claim) claims[scope] = claim;
    });

    console.log("----------------------------------CLAIMS", claims)
    return claims;
}

function isValidPerson(username) {
    return _findPerson(username) !== undefined;
}

function _findPerson(username) {
    return peopleData[username];
}

function _getClaimValue(username, person, scopeName) {
    switch (scopeName) {
        case "email":
            return person['email'] ? person['email'] : `${username}@vt.edu`;
        case "email_verified":
            return true;
        case "groupMembershipUugid":
            return person.groups;
        default:
            return person[scopeName];
    }
}

module.exports = {
    init,
    isValidPerson,
    getClaims,
};
