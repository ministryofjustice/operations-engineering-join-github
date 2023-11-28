# Web Application Security Assessment

## Context

The web application is publicly accessible on the internet, making it susceptible to various security threats.
Understanding these threats and their potential impact on Confidentiality, Integrity, and Availability (CIA) is crucial
for ensuring the application's security posture.

This assessment will be carried out in the context of current mitigations and as they apply to a PoC/Testing
Environment.

## Current Vulnerabilities

### API Endpoint POST /join-github-form

#### Impact: `HIGH`

#### Description

The API endpoint `POST /join-github-form` currently is available via the public internet.

The endpoint validates the email domain in the POST request data, and if the email domain is pre-approved the
application sends an invitation to the `ministryofjustice-test` organisation for the provided email.

Only users with access to these email addresses will be able to accept these invitations, although the invitations
themselves can be raised by anyone.

Invitations to any organisation impacts the pool of available seats for MoJs Enterprise GitHub Account. An attacker
could send multiple requests, using emails with valid domains, to drain the pool of available seats in MoJs Enterprise
GitHub Account.

#### CIA Assessment (in the context of PoC/Testing Environment)

- **Confidentiality**: `Low` - An attacker would not be able to gain access to any sensitive information through this
  attack, since they would not be able to accept these invitations to gain access.
- **Integrity**: `Low` - All invitations are raised to join `ministryofjustice-test` organisation - so identifying
  malicious invitations should be easy. Other than differentiating genuine and malicious invitations, there is no impact
  on integrity.
- **Availability**: `High` - An attacker could continuously raise these requests to constantly drain the pool of seats
  available. Meaning MoJ would find it difficult to onboard new users onto MoJs Enterprise GitHub Account, preventing
  people from performing their jobs effectively.

#### Rationale

This vulnerability is reasonably exploitable and impacts the availability of the GitHub onboarding service. Therefore,
we should implement mitigation measures before turning the service back on in the testing environment. Some mitigations
options listed below are only applicable to the testing environment. When deploying to a production environment, ensure
reasonable mitigations are in place for the service to securely run in a production environment.

#### Mitigation Suggestions

The service has been turned off temporarily whilst this concern is addressed. To mitigate this threat, I habe detailed
some suggestions below:

- [ ] Verify the user has access to the pre-approved email before raising an invitation to the MoJs Enterprise GitHub
  Account. This ensures that only our targeted users have access to raise invitations.

- [ ] Only make the service available to specific, pre-agreed MoJ network ranges. This method doesn't fix the exploit -
  but will decrease the chances of it happening, since only a more trusted user base will have access. This may also
  exclude some of the intended users from using the service.

- [ ] Whilst in the testing phases, implement logic that checks the number of users currently in
  the `ministryofjustice-test` organisation and only send invitations if below a certain number (10, for example). This
  will reduce the impact of the vulnerability being exploited. This will enable the service to be live for testing and
  development - although is not a suitable solution for production.

- [ ] Whilst in the testing phases, implement an allow list of pre-approved emails that are able to complete this
  process and raise invitations. This will enable the service to be live for testing and development - although is not a
  suitable solution for production.

- [ ] Whilst in the testing phases, implement a check for the number of pending invitations in flight and do not proceed
  if at a maximum number (5 for example). This reduces the impact of this vulnerability being exploited. This will
  enable the service to be live for testing and development - although is not a suitable solution for production.

## Decision

The system, as is, is not suitable to be deployed into the testing environment.

This is due to the system in the testing environment having a `HIGH` impact on the availability of the live GitHub
onboarding process coupled with the fact that the vulnerability is reasonably exploitable via the public internet.

In order to enable the system to be deployed into the current testing environment, mitigations will need to be
implemented in relation to the following areas:

- Minimise the impact of the vulnerability being exploited, so that it doesn't significantly affect the live GitHub
  onboarding process in a _"worst-case scenario"_ i.e. the endpoint being constantly hit.
- Decrease access to the endpoint that interacts with production resources to a more trusted group of users (
  authentication and authorisation mitigations)

Once mitigations have been implemented, the team will re-assess the system to determine whether it's suitable for the
current testing environment

### 2023-11-28 Update - Enable in Testing Environment

The system is now suitable to be deployed into a testing environment.

The original endpoint of `POST /join-github-form` (now `POST /join-github-auth0-user`) has implemented authentication
checks so that only users that have gone through a verification process can have access to the production resource.

The risks of the trusted user group abusing the system has been further mitigated by rate-limiting client requests
and signing cookies with a `SECRET_KEY` to prevent tampering.

Due to these mitigations, the system is now in a place to be re-enabled in the testing environment to allow further
assessment of the application to determine whether it's suitable for production.
