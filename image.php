<?php

class CurlRequest {
	protected $curl;

	protected $return_header = false;
	protected $header = NULL;
	protected $post = NULL;

	public function return_header($value) {
		$this->return_header = $value;
	}

	public function add_header($name, $value) {
		if($this->header === NULL) $this->header = array();
		$this->header[] = "{$name}: {$value}";
	}

	public function post_value($postfields) {
		$this->post = $postfields;
	}

	public function request($url) {
		$this->curl = curl_init();
		curl_setopt($this->curl, CURLOPT_URL, $url);
		curl_setopt($this->curl, CURLOPT_USERAGENT, "DESKTOP:MAC:10.9.4-MAVERICKS-x64(3.7.0)");
		curl_setopt($this->curl, CURLOPT_SSL_VERIFYPEER, false);
		curl_setopt($this->curl, CURLOPT_SSLVERSION, 3);
		curl_setopt($this->curl, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($this->curl, CURLOPT_FOLLOWLOCATION, true);
		curl_setopt($this->curl, CURLOPT_HEADER, $this->return_header);

		if($this->header !== NULL) {
			curl_setopt($this->curl, CURLOPT_HTTPHEADER, $this->header);
		}

		if($this->post !== NULL) {
			curl_setopt($this->curl, CURLOPT_POST, true);
			curl_setopt($this->curl, CURLOPT_POSTFIELDS, $this->post);
		}

		$result = curl_exec($this->curl);
		curl_close($this->curl);

		$this->return_header = false;
		$this->header = NULL;
		$this->post = NULL;

		return $result;
	}
}

$c = new CurlRequest;
$c->add_header("X-Line-Application", "DESKTOPMAC\t3.7.0\tMAC\t10.9.4-MAVERICKS-x64");
$c->add_header("X-Line-Access", ""); // add your token here
$output = $c->request("http://os.line.naver.jp/os/m/".$_GET["id"]);

header("Content-Type: image/jpeg");
die($output);
