import re
import os
import socket
import http.server
import ssl
from argparse import ArgumentParser

# server_cert = "-----BEGIN CERTIFICATE-----\n" \
#               "MIIDXTCCAkWgAwIBAgIJAP4LF7E72HakMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV\n"\
#               "BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX\n"\
#               "aWRnaXRzIFB0eSBMdGQwHhcNMTkwNjA3MDk1OTE2WhcNMjAwNjA2MDk1OTE2WjBF\n"\
#               "MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50\n"\
#               "ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB\n"\
#               "CgKCAQEAlzfCyv3mIv7TlLkObxunKfCdrJ/zgdANrsx0RBtpEPhV560hWJ0fEin0\n"\
#               "nIOMpJSiF9E6QsPdr6Q+eogH4XnOMU9JE+iG743N1dPfGEzJvRlyct/Ck8SswKPC\n"\
#               "9+VXsnOdZmUw9y/xtANbURA/TspvPzz3Avv382ffffrJGh7ooOmaZSCZFlSYHLZA\n"\
#               "w/XlRr0sSRbLpFGY0gXjaAV8iHHiPDYLy4kZOepjV9U51xi+IGsL4w75zuMgsHyF\n"\
#               "3nJeGYHgtGVBrkL0ZKG5udY0wcBjysjubDJC4iSlNiq2HD3fhs7j6CZddV2v845M\n"\
#               "lVKNxP0kO4Uj4D8r+5USWC8JKfAwxQIDAQABo1AwTjAdBgNVHQ4EFgQU6OE7ssfY\n"\
#               "IIPTDThiUoofUpsD5NwwHwYDVR0jBBgwFoAU6OE7ssfYIIPTDThiUoofUpsD5Nww\n"\
#               "DAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAXIlHS/FJWfmcinUAxyBd\n"\
#               "/xd5Lu8ykeru6oaUCci+Vk9lyoMMES7lQ+b/00d5x7AcTawkTil9EWpBTPTOTraA\n"\
#               "lzJMQhNKmSLk0iIoTtAJtSZgUSpIIozqK6lenxQQDsHbXKU6h+u9H6KZE8YcjsFl\n"\
#               "6vL7sw9BVotw/VxfgjQ5OSGLgoLrdVT0z5C2qOuwOgz1c7jNiJhtMdwN+cOtnJp2\n"\
#               "fuBgEYyE3eeuWogvkWoDcIA8r17Ixzkpq2oJsdvZcHZPIZShPKW2SHUsl98KDemu\n"\
#               "y0pQyExmQUbwKE4vbFb9XuWCcL9XaOHQytyszt2DeD67AipvoBwVU7/LBOvqnsmy\n"\
#               "hA==\n"\
#               "-----END CERTIFICATE-----\n"

# server_key = "-----BEGIN PRIVATE KEY-----\n"\
#              "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCXN8LK/eYi/tOU\n"\
#              "uQ5vG6cp8J2sn/OB0A2uzHREG2kQ+FXnrSFYnR8SKfScg4yklKIX0TpCw92vpD56\n"\
#              "iAfhec4xT0kT6Ibvjc3V098YTMm9GXJy38KTxKzAo8L35Veyc51mZTD3L/G0A1tR\n"\
#              "ED9Oym8/PPcC+/fzZ999+skaHuig6ZplIJkWVJgctkDD9eVGvSxJFsukUZjSBeNo\n"\
#              "BXyIceI8NgvLiRk56mNX1TnXGL4gawvjDvnO4yCwfIXecl4ZgeC0ZUGuQvRkobm5\n"\
#              "1jTBwGPKyO5sMkLiJKU2KrYcPd+GzuPoJl11Xa/zjkyVUo3E/SQ7hSPgPyv7lRJY\n"\
#              "Lwkp8DDFAgMBAAECggEAfBhAfQE7mUByNbxgAgI5fot9eaqR1Nf+QpJ6X2H3KPwC\n"\
#              "02sa0HOwieFwYfj6tB1doBoNq7i89mTc+QUlIn4pHgIowHO0OGawomeKz5BEhjCZ\n"\
#              "4XeLYGSoODary2+kNkf2xY8JTfFEcyvGBpJEwc4S2VyYgRRx+IgnumTSH+N5mIKZ\n"\
#              "SXWNdZIuHEmkwod+rPRXs6/r+PH0eVW6WfpINEbr4zVAGXJx2zXQwd2cuV1GTJWh\n"\
#              "cPVOXLu+XJ9im9B370cYN6GqUnR3fui13urYbnWnEf3syvoH/zuZkyrVChauoFf8\n"\
#              "8EGb74/HhXK7Q2s8NRakx2c7OxQifCbcy03liUMmyQKBgQDFAob5B/66N4Q2cq/N\n"\
#              "MWPf98kYBYoLaeEOhEJhLQlKk0pIFCTmtpmUbpoEes2kCUbH7RwczpYko8tlKyoB\n"\
#              "6Fn6RY4zQQ64KZJI6kQVsjkYpcP/ihnOY6rbds+3yyv+4uPX7Eh9sYZwZMggE19M\n"\
#              "CkFHkwAjiwqhiiSlUxe20sWmowKBgQDEfx4lxuFzA1PBPeZKGVBTxYPQf+DSLCre\n"\
#              "ZFg3ZmrxbCjRq1O7Lra4FXWD3dmRq7NDk79JofoW50yD8wD7I0B7opdDfXD2idO8\n"\
#              "0dBnWUKDr2CAXyoLEINce9kJPbx4kFBQRN9PiGF7VkDQxeQ3kfS8CvcErpTKCOdy\n"\
#              "5wOwBTwJdwKBgDiTFTeGeDv5nVoVbS67tDao7XKchJvqd9q3WGiXikeELJyuTDqE\n"\
#              "zW22pTwMF+m3UEAxcxVCrhMvhkUzNAkANHaOatuFHzj7lyqhO5QPbh4J3FMR0X9X\n"\
#              "V8VWRSg+jA/SECP9koOl6zlzd5Tee0tW1pA7QpryXscs6IEhb3ns5R2JAoGAIkzO\n"\
#              "RmnhEOKTzDex611f2D+yMsMfy5BKK2f4vjLymBH5TiBKDXKqEpgsW0huoi8Gq9Uu\n"\
#              "nvvXXAgkIyRYF36f0vUe0nkjLuYAQAWgC2pZYgNLJR13iVbol0xHJoXQUHtgiaJ8\n"\
#              "GLYFzjHQPqFMpSalQe3oELko39uOC1CoJCHFySECgYBeycUnRBikCO2n8DNhY4Eg\n"\
#              "9Y3oxcssRt6ea5BZwgW2eAYi7/XqKkmxoSoOykUt3MJx9+EkkrL17bxFSpkj1tvL\n"\
#              "qvxn7egtsKjjgGNAxwXC4MwCvhveyUQQxtQb8AqGrGqo4jEEN0L15cnP38i2x1Uo\n"\
#              "muhfskWf4MABV0yTUaKcGg==\n"\
#              "-----END PRIVATE KEY-----\n"


server_cert = "-----BEGIN CERTIFICATE-----\n" \
            "MIID+zCCAuOgAwIBAgIUQs/7PujFhdl0JvP9cv1rAQJTtrgwDQYJKoZIhvcNAQEL\n"\
            "BQAwgYwxCzAJBgNVBAYTAkNOMRAwDgYDVQQIDAdKaWFuZ3N1MQ8wDQYDVQQHDAZT\n"\
            "dXpob3UxEjAQBgNVBAoMCUVzcHJlc3NpZjEMMAoGA1UECwwDY29tMRYwFAYDVQQD\n"\
            "DA0xOTIuMTY4LjQzLjcyMSAwHgYJKoZIhvcNAQkBFhFlc3BAZXNwcmVzc2lmLmNv\n"\
            "bTAeFw0yMDA4MTUwNTAyMThaFw0yMTA4MTUwNTAyMThaMIGMMQswCQYDVQQGEwJD\n"\
            "TjEQMA4GA1UECAwHSmlhbmdzdTEPMA0GA1UEBwwGU3V6aG91MRIwEAYDVQQKDAlF\n"\
            "c3ByZXNzaWYxDDAKBgNVBAsMA2NvbTEWMBQGA1UEAwwNMTkyLjE2OC40My43MjEg\n"\
            "MB4GCSqGSIb3DQEJARYRZXNwQGVzcHJlc3NpZi5jb20wggEiMA0GCSqGSIb3DQEB\n"\
            "AQUAA4IBDwAwggEKAoIBAQC6RUX6nPXPrVg2XUajgq7SiKLTh2hvS1/lu47bVMPa\n"\
            "vdTadNz19qk2brj1pWESPGkDOh+oC/zd1oOHAUztbAOz5ZgwIdt0e4N3G3BL0E/s\n"\
            "GvjuF77jh19WOcQGoSf2pxRzxmWZGEdtEk+zg1/KkgoAYRUjzikmVsJUIg4kI7rI\n"\
            "vpy+ftW9axLpIvseFOtYaYREQGNIaVWLZRuK5kocMBd4W9taRm4inNO+aRGXCk8v\n"\
            "/q33tnpv2tNXKB43lNuvHH4HfsiVnM/QVDAceG77wAadaJvRN88MXPTc4ewdW8qI\n"\
            "rL4oIrTGVfZcOYYwJe8R3HqMWQGsu1LHdo+DFuyuHw2VAgMBAAGjUzBRMB0GA1Ud\n"\
            "DgQWBBRyAw3JE4DHCpZ24/vqf23XdXzOAzAfBgNVHSMEGDAWgBRyAw3JE4DHCpZ2\n"\
            "4/vqf23XdXzOAzAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQC5\n"\
            "fiCjJmaGDz8po6/1BsEKC/bhXK6+eihMcyc8WJ+WzZ8B7UdCbNqWRBTG4T/5Rijj\n"\
            "LClTMlw42Tvzhiq85Wo1UgzSPkSEYz1xLnsBd3D9dqOKjBBZTWch99F1kgiwtrG6\n"\
            "dpHiUZDouTWXl/4EkBW9F0RYojsMRkFSG29m0c7YLdHUafUU5wiHWl5XPzbiQHhG\n"\
            "iZggbtzXeSWKEYaz+T5Y0lkp43FmgMOgz8vm9iTb7GMrCkbZ1OPrMXsKbjkld8nj\n"\
            "moL9syVackOSNMliEnUBzDoXWFbEgi+HwUIMPuUPV0vUcs1dDgTZfyCnwCIv5/3K\n"\
            "+N/HQtqGL/KZo7EzMN5b\n"\
              "-----END CERTIFICATE-----\n"

server_key = "-----BEGIN PRIVATE KEY-----\n"\
            "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC6RUX6nPXPrVg2\n"\
            "XUajgq7SiKLTh2hvS1/lu47bVMPavdTadNz19qk2brj1pWESPGkDOh+oC/zd1oOH\n"\
            "AUztbAOz5ZgwIdt0e4N3G3BL0E/sGvjuF77jh19WOcQGoSf2pxRzxmWZGEdtEk+z\n"\
            "g1/KkgoAYRUjzikmVsJUIg4kI7rIvpy+ftW9axLpIvseFOtYaYREQGNIaVWLZRuK\n"\
            "5kocMBd4W9taRm4inNO+aRGXCk8v/q33tnpv2tNXKB43lNuvHH4HfsiVnM/QVDAc\n"\
            "eG77wAadaJvRN88MXPTc4ewdW8qIrL4oIrTGVfZcOYYwJe8R3HqMWQGsu1LHdo+D\n"\
            "FuyuHw2VAgMBAAECggEACJvtCRE6FzgmzJRxEFuY4ugnxmkKvaIZM5AAoUiAqNp/\n"\
            "PP2LvN6CoZ5qdAgJvYMHQ3vrPKQZMtOYTqQTvyFv5l+lMgxOjUqsH9Qn04k0OHBi\n"\
            "svZr/y4hjOWslrXaF/9O5a70wSerHXJsNprK0Z0AU1YpWPdNVZVK9AKC7s6r8l0w\n"\
            "xpuFb7KZwg7bb4Xrm7Q+OO+ql/3Umbghnj6J/VaBlr5MbmcXaNGuVoe43iZXK3RO\n"\
            "Q42LowG6AOWd8vVyMUUPPALllj3tfMVUYnY4knFILzXOfxUWM/ewU72v2HaK4NVc\n"\
            "tM7QBAgRHlMGBD6TD2Bd03BRHmq6lCShrSL+WKEp/QKBgQDfTrfSGUp//fjWssw8\n"\
            "KfMXnA2XNTSDdebFeJHPWnBjcnF7tyxzcp3g1tq4XAyGGaS5jSGlRERBuVw6O6zN\n"\
            "Wn02COFqkyIDRY13tgvEc3sAULU74u4jqUEVm0KNiq3spcPGAoui+Soa6IJtJRD2\n"\
            "finBEC+6CWRH/e3kXi83dTMbRwKBgQDVinWfDFUwZsKRabuH6cNsz5eqNn+RTEhi\n"\
            "4ucuHGSZzUyRGruBf6UYPi4ipMnH6+JNrXMt3aIljUNo4Sp5GUU6jO3cWZKSKrJW\n"\
            "t4JMqcAcp6QaITOrzh2fPbvNRtXQap96oC3yNJzCJghfrSJiJFqkNA6GimuqHILa\n"\
            "J6M1dyrGQwKBgQCvAGHOpUNdSwvYNgcYn0eDGSkNdwTQgXV5DCQ4/AdX6DhHXCXZ\n"\
            "09kmezqtgHXQIgiV4aScgAN9/mXovRuPU3sM/aiqfOQK7FcRmfle26FpfdaKOC2o\n"\
            "hNwcsrBVfHkRHFdwtk34SoxUyiJspr/EbNsMEkNU6EdOpBHrBmS6cX67wQKBgQCs\n"\
            "yE/L1YrIkx0z072th3RdAsvRKi+mPXcErFwqb0bnO7qMXnkBm2rWZtmlpniujyqZ\n"\
            "d5MOtZqRj+/PWQGo4s2lRorgFIoIQwvyJqIDrgaIKQ0bJ2pLxYcqZiUjQAGZlexc\n"\
            "qGcE55U/cs6ru8dqacf9vTFTo4TiLBektRXWGQo/SQKBgQDfPCRR5rAVMBVKvGJf\n"\
            "e2QnEA3vaaNegdRmxKNCdVLFUj1JRyJf436wgKCFO/lRIzB5eRSdjWqdkKTAVOnY\n"\
            "1v9hlNyj6/8lU88AbeC2drt5Zf5aKUvptqKRRKjjpafmXtq7vzZAsWtEVg7QFYSd\n"\
            "DEV0rUOZH7e61W6qhlFCxgSjXg==\n"\
             "-----END PRIVATE KEY-----\n"

def get_my_ip():
    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.connect(("8.8.8.8", 80))
    my_ip = s1.getsockname()[0]
    s1.close()
    return my_ip


def create_file(server_file, file_data):
    with open(server_file, "w+") as file:
        file.write(file_data)


def get_ca_cert(ota_image_dir):
    os.chdir(ota_image_dir)
    server_file = os.path.join(ota_image_dir, "server_cert.pem")
    create_file(server_file, server_cert)

    key_file = os.path.join(ota_image_dir, "server_key.pem")
    create_file(key_file, server_key)
    return server_file, key_file


def https_request_handler():
    """
    Returns a request handler class that handles broken pipe exception
    """
    class RequestHandler(http.server.SimpleHTTPRequestHandler):
        def finish(self):
            try:
                if not self.wfile.closed:
                    self.wfile.flush()
                    self.wfile.close()
            except socket.error:
                pass
            self.rfile.close()

        def handle(self):
            try:
                http.server.BaseHTTPRequestHandler.handle(self)
            except socket.error:
                pass

    return RequestHandler


def start_https_server(ota_image_dir, server_ip, server_port):
    server_file, key_file = get_ca_cert(ota_image_dir)
    requestHandler = https_request_handler()
    httpd = http.server.HTTPServer((server_ip, server_port),
                                      requestHandler)

    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   keyfile=key_file,
                                   certfile=server_file, server_side=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        # A request to terminate has been received, stop the server
        print("\nShutting down...")
        httpd.socket.close()


if __name__ == '__main__':
    cli = ArgumentParser(description='Example Python Application')
    cli.add_argument(
    "-p", "--port", type=int, metavar="server_port", dest="server_port", default=8070)
    arguments = cli.parse_args()
    host_ip = get_my_ip()
    print(("Starting server: {0}://{1}:{2}".format("https", host_ip, arguments.server_port)))
    start_https_server(os.getcwd(), host_ip, arguments.server_port)
