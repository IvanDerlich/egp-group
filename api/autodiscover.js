module.exports = async (req, res) => {
  // Set appropriate headers
  res.setHeader('Content-Type', 'application/xml; charset=utf-8');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST');
  
  // Handle OPTIONS for CORS
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  let emailAddress = 'contacto@egpgroup.com.ar'; // default

  // Try to parse email from POST body (Outlook sends XML)
  if (req.method === 'POST') {
    try {
      let body = '';
      
      // Check if body is already parsed
      if (req.body) {
        if (typeof req.body === 'string') {
          body = req.body;
        } else if (typeof req.body === 'object') {
          // If it's already parsed as JSON, try to stringify and look for email
          body = JSON.stringify(req.body);
        }
      }
      
      // Extract email from XML like <EMailAddress>user@domain.com</EMailAddress>
      if (body) {
        const emailMatch = body.match(/<EMailAddress>([^<]+)<\/EMailAddress>/i);
        if (emailMatch && emailMatch[1]) {
          emailAddress = emailMatch[1];
        }
      }
    } catch (e) {
      // Use default email
      console.error('Error parsing email:', e);
    }
  }
  
  // Also check query parameter for GET requests
  if (req.query && req.query.email) {
    emailAddress = req.query.email;
  }

  // Outlook Autodiscover XML response
  const autodiscoverXml = `<?xml version="1.0" encoding="utf-8"?>
<Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/responseschema/2006">
  <Response xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a">
    <Account>
      <AccountType>email</AccountType>
      <Action>settings</Action>
      <Protocol>
        <Type>IMAP</Type>
        <Server>business117.web-hosting.com</Server>
        <Port>993</Port>
        <LoginName>${emailAddress}</LoginName>
        <SPA>off</SPA>
        <SSL>on</SSL>
        <AuthRequired>on</AuthRequired>
      </Protocol>
      <Protocol>
        <Type>SMTP</Type>
        <Server>business117.web-hosting.com</Server>
        <Port>465</Port>
        <LoginName>${emailAddress}</LoginName>
        <SPA>off</SPA>
        <SSL>on</SSL>
        <AuthRequired>on</AuthRequired>
      </Protocol>
    </Account>
  </Response>
</Autodiscover>`;

  res.status(200).send(autodiscoverXml);
};
