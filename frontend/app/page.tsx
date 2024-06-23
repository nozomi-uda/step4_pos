// app/page.tsx

'use client';

import { useState } from 'react';

export default function Home() {
  // 状態管理
  const [barcode, setBarcode] = useState('');
  const [product, setProduct] = useState<Product | null>(null);
  const [purchaseList, setPurchaseList] = useState<Product[]>([]);
  const [quantity, setQuantity] = useState<number>(1);
  const [totalPrice, setTotalPrice] = useState<number>(0);
  const [showTotalPopup, setShowTotalPopup] = useState<boolean>(false);
  const [showQuantityPopup, setShowQuantityPopup] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  // 商品マスタから商品情報を取得
const queryProductMaster = async (code: string): Promise<Product | null> => {
  try {
    const response = await fetch(`http://localhost:8000/products/${code}`);
    if (response.ok) {
      const product = await response.json();
      return product;
    } else {
      return null;
    }
  } catch (error) {
    console.error('商品情報の取得に失敗しました:', error);
    return null;
  }
};

  // 商品情報の読み込み
  const handleLoadProduct = async () => {
    // 仮で商品コードを example-code に設定
    const scannedCode = 'example-code';
    setBarcode(scannedCode);

    const fetchedProduct = await queryProductMaster(scannedCode);
    setProduct(fetchedProduct);
    if (!fetchedProduct) {
      alert('商品がマスタ未登録です');
    }
  };

  // 購入リストに商品を追加
  const handleAddToList = () => {
    if (product) {
      const existingProductIndex = purchaseList.findIndex(item => item.code === product.code);
      if (existingProductIndex >= 0) {
        // 既存の商品を更新
        const updatedList = [...purchaseList];
        updatedList[existingProductIndex].quantity += 1;
        setPurchaseList(updatedList);
      } else {
        // 新しい商品を追加
        setPurchaseList([...purchaseList, { ...product, quantity: 1 }]);
      }
      setProduct(null);
      setBarcode('');
    }
  };

  // 購入リストから商品を削除
  const handleRemoveProduct = (code: string) => {
    const updatedList = purchaseList.filter(item => item.code !== code);
    setPurchaseList(updatedList);
    setSelectedProduct(null);
  };

  // 購入処理
const handlePurchase = async () => {
  const total = calculateTotal();
  setTotalPrice(total);
  try {
    const response = await fetch('http://localhost:8000/transactions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        purchaseList: purchaseList.map(item => ({
          code: item.code,
          name: item.name,
          quantity: item.quantity,
          price: item.price,
        })),
        total,
      }),
    });
    if (response.ok) {
      console.log('取引が正常に格納されました');
    } else {
      console.error('取引の格納に失敗しました');
    }
  } catch (error) {
    console.error('取引の格納中にエラーが発生しました:', error);
  }
  setShowTotalPopup(true);
};

  // 合計金額を計算
  const calculateTotal = () => {
    return purchaseList.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };

  // ポップアップを閉じてリセット
  const handleClosePopup = () => {
    setShowTotalPopup(false);
    setPurchaseList([]);
    setProduct(null);
    setBarcode('');
    setTotalPrice(0);
  };

  // 数量変更ポップアップを表示
  const handleQuantityChange = (product: Product) => {
    setSelectedProduct(product);
    setQuantity(product.quantity);
    setShowQuantityPopup(true);
  };

  // 数量を更新
  const handleQuantityUpdate = () => {
    if (quantity < 1 || quantity > 99) {
      setErrorMessage('数量は1~99までの値を選択してください');
    } else {
      if (selectedProduct) {
        const updatedList = purchaseList.map(item =>
          item.code === selectedProduct.code ? { ...item, quantity } : item
        );
        setPurchaseList(updatedList);
        setShowQuantityPopup(false);
        setSelectedProduct(null);
        setProduct(null);
        setBarcode('');
        setQuantity(1);
        setErrorMessage('');
      }
    }
  };

  return (
    <div className="flex min-h-screen p-4 bg-white">
      {/* 左側の列 */}
      <div className="left-column">
        <input
          type="text"
          value={barcode}
          onChange={(e) => setBarcode(e.target.value)}
          placeholder="商品コード"
          className="border rounded w-full px-2 py-1"
        />
        <button
          onClick={handleLoadProduct}
          className="bg-blue-500 text-white w-full py-2 rounded"
        >
          商品コード読み込み
        </button>
        <div className="mb-4">
          <label className="block mb-1">名称:</label>
          <input
            type="text"
            value={product ? product.name : ''}
            readOnly
            className="border rounded w-full px-2 py-1"
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1">単価:</label>
          <input
            type="text"
            value={product ? `¥${product.price}` : ''}
            readOnly
            className="border rounded w-full px-2 py-1"
          />
        </div>
        <button
          onClick={handleAddToList}
          className="bg-green-500 text-white w-full py-2 rounded"
        >
          追加
        </button>
      </div>

      {/* 右側の列 */}
      <div className="right-column">
        <h2 className="text-xl mb-2 text-center">購入品目リスト:</h2>
        <div className="mb-4 border p-4 rounded flex-1 overflow-auto">
          <ul className="purchase-list">
            {purchaseList.map((item, index) => (
              <li key={index} className="purchase-list-item">
                <div>
                  {item.name} - {item.quantity}個 - ¥{item.price} - 合計: ¥{item.price * item.quantity}
                </div>
                <button
                  onClick={() => handleQuantityChange(item)}
                  className="bg-yellow-500 text-white px-2 py-1 rounded ml-4"
                >
                  数量変更
                </button>
                <button
                  onClick={() => handleRemoveProduct(item.code)}
                  className="bg-red-500 text-white px-2 py-1 rounded ml-2"
                >
                  削除
                </button>
              </li>
            ))}
          </ul>
        </div>
        <button onClick={handlePurchase} className="purchase-button">購入</button>
      </div>

      {/* 合計金額ポップアップ */}
      {showTotalPopup && (
        <div className="popup-overlay">
          <div className="popup-content">
            <h2 className="text-2xl mb-4">合計金額</h2>
            <p>税込: ¥{totalPrice}</p>
            <p>税抜: ¥{Math.round(totalPrice / 1.1)}</p>
            <button onClick={handleClosePopup} className="bg-blue-500 text-white w-full py-2 rounded mt-4">OK</button>
          </div>
        </div>
      )}

      {/* 数量変更ポップアップ */}
      {showQuantityPopup && (
        <div className="popup-overlay">
          <div className="popup-content">
            <h2 className="text-2xl mb-4">数量変更</h2>
            {errorMessage && <p className="text-red-500 mb-4">{errorMessage}</p>}
            <input
              type="number"
              min="1"
              max="99"
              value={quantity}
              onChange={(e) => setQuantity(Number(e.target.value))}
              className="border rounded w-full mb-4 p-2"
            />
            <button
              onClick={handleQuantityUpdate}
              className="bg-blue-500 text-white w-full py-2 rounded"
            >
              更新
            </button>
            <button
              onClick={() => setShowQuantityPopup(false)}
              className="bg-gray-500 text-white w-full py-2 rounded mt-2"
            >
              キャンセル
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// 商品インターフェース
interface Product {
  name: string;
  code: string;
  price: number;
  quantity: number;
}