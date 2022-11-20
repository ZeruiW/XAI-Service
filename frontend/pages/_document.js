import React from "react";
import Document, { Html, Head, Main, NextScript } from "next/document";

class MyDocument extends Document {
	render() {
		return (
			<Html lang="en" className="theme-compiled dark">
				<Head>
					<link rel="preconnect" href="https://fonts.googleapis.com" />
					<link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="true" />
				</Head>
				<body className={`antialiased text-lg leading-base`}>
					<Main />
					<NextScript />
				</body>
			</Html>
		);
	}
}

export default MyDocument;
